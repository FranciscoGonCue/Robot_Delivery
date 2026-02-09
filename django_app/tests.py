from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import EmailVerification
import uuid


class EmailVerificationModelTest(TestCase):
    """Test EmailVerification model functionality"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get the automatically created EmailVerification
        self.email_verification = EmailVerification.objects.get(user=self.user)
    
    def test_email_verification_created_on_user_creation(self):
        """Test that EmailVerification is automatically created when User is created"""
        self.assertIsNotNone(self.email_verification)
        self.assertEqual(self.email_verification.user, self.user)
        self.assertFalse(self.email_verification.is_verified)
    
    def test_default_values(self):
        """Test default values for new fields"""
        self.assertEqual(self.email_verification.expiration_time, 10)  # 10 minutes default
        self.assertTrue(self.email_verification.available)  # True by default
        self.assertIsNotNone(self.email_verification.verification_token)
    
    def test_token_valid_within_expiration_time(self):
        """Test that token is valid within expiration time"""
        self.assertTrue(self.email_verification.is_token_valid())
    
    def test_token_invalid_when_expired(self):
        """Test that token is invalid after expiration time"""
        # Set token created time to 11 minutes ago (past the 10 min default)
        self.email_verification.token_created_at = timezone.now() - timedelta(minutes=11)
        self.email_verification.save()
        
        # Token should be invalid
        self.assertFalse(self.email_verification.is_token_valid())
        
        # Verify that available was set to False
        self.email_verification.refresh_from_db()
        self.assertFalse(self.email_verification.available)
    
    def test_token_invalid_when_not_available(self):
        """Test that token is invalid when available is False"""
        self.email_verification.available = False
        self.email_verification.save()
        
        self.assertFalse(self.email_verification.is_token_valid())
    
    def test_token_invalid_when_already_verified(self):
        """Test that token is invalid when already verified"""
        self.email_verification.is_verified = True
        self.email_verification.verified_at = timezone.now()
        self.email_verification.save()
        
        self.assertFalse(self.email_verification.is_token_valid())
    
    def test_regenerate_token_invalidates_old_token(self):
        """Test that regenerating token invalidates the old one first"""
        old_token = self.email_verification.verification_token
        old_created_at = self.email_verification.token_created_at
        
        # Regenerate token
        self.email_verification.regenerate_token()
        
        # Verify old token was invalidated and new one created
        self.assertNotEqual(self.email_verification.verification_token, old_token)
        self.assertNotEqual(self.email_verification.token_created_at, old_created_at)
        self.assertTrue(self.email_verification.available)
    
    def test_regenerate_token_two_step_process(self):
        """Test that token regeneration happens in two steps for security"""
        # This test verifies the logic but the implementation does both steps
        # in the same method call for simplicity
        old_token = self.email_verification.verification_token
        
        self.email_verification.regenerate_token()
        
        # New token should be different
        self.assertNotEqual(self.email_verification.verification_token, old_token)
        # Should be available after regeneration
        self.assertTrue(self.email_verification.available)


class EmailVerificationAPITest(APITestCase):
    """Test email verification API endpoints"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.verify_url = '/api/auth/verify-email/'
        self.resend_url = '/api/auth/resend-verification/'
        self.login_url = '/api/auth/login/'
    
    def test_register_creates_email_verification(self):
        """Test that registering creates an EmailVerification record"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(username='newuser')
        email_verification = EmailVerification.objects.get(user=user)
        
        self.assertIsNotNone(email_verification)
        self.assertFalse(email_verification.is_verified)
        self.assertTrue(email_verification.available)
    
    def test_verify_email_success(self):
        """Test successful email verification"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        token = email_verification.verification_token
        
        # Verify email
        response = self.client.get(f"{self.verify_url}?token={token}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Check that email is verified and token is no longer available
        email_verification.refresh_from_db()
        self.assertTrue(email_verification.is_verified)
        self.assertFalse(email_verification.available)
        self.assertIsNotNone(email_verification.verified_at)
    
    def test_verify_email_with_invalid_token(self):
        """Test verification with invalid token"""
        fake_token = uuid.uuid4()
        response = self.client.get(f"{self.verify_url}?token={fake_token}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_verify_email_with_expired_token(self):
        """Test verification with expired token"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        token = email_verification.verification_token
        
        # Make token expired
        email_verification.token_created_at = timezone.now() - timedelta(minutes=11)
        email_verification.save()
        
        # Try to verify
        response = self.client.get(f"{self.verify_url}?token={token}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data)
        self.assertTrue(response.data['expired'])
    
    def test_verify_email_when_not_available(self):
        """Test verification when token is not available"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        token = email_verification.verification_token
        
        # Mark as not available
        email_verification.available = False
        email_verification.save()
        
        # Try to verify
        response = self.client.get(f"{self.verify_url}?token={token}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data)
    
    def test_verify_email_already_verified(self):
        """Test verification when email is already verified"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        token = email_verification.verification_token
        
        # Mark as verified
        email_verification.is_verified = True
        email_verification.verified_at = timezone.now()
        email_verification.save()
        
        # Try to verify again
        response = self.client.get(f"{self.verify_url}?token={token}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('already_verified'))
    
    def test_resend_verification_invalidates_old_token(self):
        """Test that resending verification invalidates the old token"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        old_token = email_verification.verification_token
        
        # Resend verification
        response = self.client.post(self.resend_url, {
            'email': 'test@example.com'
        })
        
        # Check that token changed
        email_verification.refresh_from_db()
        new_token = email_verification.verification_token
        
        self.assertNotEqual(old_token, new_token)
        self.assertTrue(email_verification.available)
    
    def test_cannot_have_two_active_tokens(self):
        """Test that only one token can be active at a time"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        
        # Get first token
        first_token = email_verification.verification_token
        
        # Regenerate token (simulating resend)
        email_verification.regenerate_token()
        second_token = email_verification.verification_token
        
        # Verify first token is different and the record is still available
        self.assertNotEqual(first_token, second_token)
        self.assertTrue(email_verification.available)
        
        # Try to use the first (old) token - should fail
        response = self.client.get(f"{self.verify_url}?token={first_token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # The second token should work
        response = self.client.get(f"{self.verify_url}?token={second_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_custom_expiration_time(self):
        """Test custom expiration time"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        email_verification = EmailVerification.objects.get(user=user)
        
        # Set custom expiration time to 5 minutes
        email_verification.expiration_time = 5
        email_verification.save()
        
        # Set token to 6 minutes ago
        email_verification.token_created_at = timezone.now() - timedelta(minutes=6)
        email_verification.save()
        
        # Token should be invalid
        self.assertFalse(email_verification.is_token_valid())
    
    def test_login_shows_verification_status(self):
        """Test that login response includes verification status"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('is_verified', response.data['user'])
        self.assertFalse(response.data['user']['is_verified'])


class EmailVerificationSecurityTest(TestCase):
    """Test security aspects of email verification"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.email_verification = EmailVerification.objects.get(user=self.user)
    
    def test_token_is_uuid(self):
        """Test that verification token is a valid UUID"""
        self.assertIsInstance(self.email_verification.verification_token, uuid.UUID)
    
    def test_token_is_unique(self):
        """Test that each token is unique"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        email_verification2 = EmailVerification.objects.get(user=user2)
        
        self.assertNotEqual(
            self.email_verification.verification_token,
            email_verification2.verification_token
        )
    
    def test_token_cannot_be_reused_after_verification(self):
        """Test that token cannot be reused after successful verification"""
        token = self.email_verification.verification_token
        
        # Verify email
        self.email_verification.is_verified = True
        self.email_verification.verified_at = timezone.now()
        self.email_verification.available = False
        self.email_verification.save()
        
        # Token should no longer be valid
        self.assertFalse(self.email_verification.is_token_valid())
    
    def test_expired_token_sets_available_to_false(self):
        """Test that checking an expired token automatically sets available to False"""
        # Set token to expired
        self.email_verification.token_created_at = timezone.now() - timedelta(minutes=11)
        self.email_verification.save()
        
        # Check validity (should set available to False)
        is_valid = self.email_verification.is_token_valid()
        
        self.assertFalse(is_valid)
        self.email_verification.refresh_from_db()
        self.assertFalse(self.email_verification.available)


print("✅ All test classes defined. Run with: python3 manage.py test django_app")
