from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from .models import EmailVerification
from .email_service import send_verification_email, send_verification_success_email


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user (email verification is optional)
    Body: {"username": "user1", "email": "user@example.com", "password": "pass123"}
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if email and User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username=username,
            email=email or '',
            password=password
        )
        
        email_verification = EmailVerification.objects.get(user=user)
        
        email_sent = False
        if email:
            frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
            email_sent = send_verification_email(user, email_verification.verification_token, frontend_url)
        
        return Response({
            'success': True,
            'message': 'User registered successfully. You can now login.' + 
                      (' Check your email to verify your account.' if email else ''),
            'email_sent': email_sent,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_verified': False
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login and get JWT tokens (email verification is optional)
    Body: {"username": "user1", "password": "pass123"}
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if email is verified (but don't block login)
        try:
            email_verification = EmailVerification.objects.get(user=user)
            is_verified = email_verification.is_verified
        except EmailVerification.DoesNotExist:
            # If no verification record exists, create one
            email_verification = EmailVerification.objects.create(user=user)
            is_verified = False
        
        # Generate tokens (regardless of verification status)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_verified': is_verified
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout and blacklist refresh token
    Body: {"refresh": "refresh_token_here"}
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
        
    except TokenError:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user info
    """
    user = request.user
    try:
        email_verification = EmailVerification.objects.get(user=user)
        is_verified = email_verification.is_verified
    except EmailVerification.DoesNotExist:
        is_verified = False
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_verified': is_verified
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user email with token
    Query params: ?token=<verification_token>
    """
    try:
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'error': 'Verification token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the verification record
        try:
            email_verification = EmailVerification.objects.get(verification_token=token)
        except EmailVerification.DoesNotExist:
            return Response({
                'error': 'Invalid verification token'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already verified
        if email_verification.is_verified:
            return Response({
                'success': True,
                'message': 'Email already verified',
                'already_verified': True
            }, status=status.HTTP_200_OK)
        
        # Check if token is available
        if not email_verification.available:
            return Response({
                'error': 'Verification token has expired',
                'message': 'This verification link is no longer available. Please request a new verification email.',
                'expired': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is still valid
        if not email_verification.is_token_valid():
            return Response({
                'error': 'Verification token has expired',
                'message': 'Please request a new verification email',
                'expired': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the email
        email_verification.is_verified = True
        email_verification.verified_at = timezone.now()
        email_verification.available = False  # Mark as unavailable after use
        email_verification.save()
        
        # Send confirmation email
        send_verification_success_email(email_verification.user)
        
        return Response({
            'success': True,
            'message': 'Email verified successfully! You can now login.',
            'user': {
                'username': email_verification.user.username,
                'email': email_verification.user.email
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend verification email
    Body: {"email": "user@example.com"} or {"username": "user1"}
    """
    try:
        email = request.data.get('email')
        username = request.data.get('username')
        
        if not email and not username:
            return Response({
                'error': 'Email or username is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user
        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user has email
        if not user.email:
            return Response({
                'error': 'No email associated with this account',
                'message': 'Please add an email to your profile first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create verification record
        email_verification, created = EmailVerification.objects.get_or_create(user=user)
        
        # Check if already verified
        if email_verification.is_verified:
            return Response({
                'error': 'Email already verified',
                'message': 'Your email is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Regenerate token
        email_verification.regenerate_token()
        
        # Send verification email
        frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
        email_sent = send_verification_email(user, email_verification.verification_token, frontend_url)
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Verification email sent successfully',
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to send verification email',
                'message': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile
    Body: {"email": "new@example.com"}
    """
    try:
        user = request.user
        email = request.data.get('email')
        
        if email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({
                    'error': 'Email already in use by another account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update email
            old_email = user.email
            user.email = email
            user.save()
            
            # If email changed, mark as unverified and send new verification
            if old_email != email:
                email_verification, created = EmailVerification.objects.get_or_create(user=user)
                email_verification.is_verified = False
                email_verification.regenerate_token()
                
                # Send verification email
                frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
                send_verification_email(user, email_verification.verification_token, frontend_url)
        
        # Get current verification status
        try:
            email_verification = EmailVerification.objects.get(user=user)
            is_verified = email_verification.is_verified
        except EmailVerification.DoesNotExist:
            is_verified = False
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_verified': is_verified
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password
    Body: {"current_password": "old123", "new_password": "new123"}
    """
    try:
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'error': 'Current password and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        if len(new_password) < 6:
            return Response({
                'error': 'New password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_email_verification(request):
    """
    Request email verification for current user
    """
    try:
        user = request.user
        
        # Check if user has email
        if not user.email:
            return Response({
                'error': 'No email associated with your account',
                'message': 'Please add an email to your profile first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create verification record
        email_verification, created = EmailVerification.objects.get_or_create(user=user)
        
        # Check if already verified
        if email_verification.is_verified:
            return Response({
                'success': True,
                'message': 'Your email is already verified',
                'already_verified': True
            }, status=status.HTTP_200_OK)
        
        # Regenerate token
        email_verification.regenerate_token()
        
        # Send verification email
        frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
        email_sent = send_verification_email(user, email_verification.verification_token, frontend_url)
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Verification email sent successfully. Please check your inbox.',
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Failed to send verification email',
                'message': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
