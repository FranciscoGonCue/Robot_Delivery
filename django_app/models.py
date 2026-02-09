from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from datetime import timedelta
from django.utils import timezone


class UserKeenonConfig(models.Model):
    """Configuración de API de Keenon por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='keenon_config')
    
    # Credenciales de Keenon
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    store_id = models.CharField(max_length=100)
    scene_code = models.CharField(max_length=100, default='HU29fr')
    
    # Token de acceso
    access_token = models.CharField(max_length=500, blank=True, null=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_keenon_configs'
        verbose_name = 'User Keenon Config'
        verbose_name_plural = 'User Keenon Configs'
    
    def __str__(self):
        return f"{self.user.username} - Keenon Config"
    
    def is_token_valid(self):
        """Check if token is still valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at


class Endpoint(models.Model):
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='endpoints')
    name = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET')
    path = models.CharField(max_length=500)  # Without base URL
    params = models.TextField(blank=True, null=True)  # JSON string
    body = models.TextField(blank=True, null=True)  # JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'endpoints'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.method} - {self.name}"


class EmailVerification(models.Model):
    """Model to store email verification tokens"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    token_created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expiration_time = models.IntegerField(default=10, help_text='Token expiration time in minutes')
    available = models.BooleanField(default=True, help_text='Token availability status')
    
    class Meta:
        db_table = 'email_verifications'
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def __str__(self):
        return f"{self.user.username} - {'Verified' if self.is_verified else 'Pending'}"
    
    def is_token_valid(self):
        """Check if token is still valid based on expiration_time"""
        if self.is_verified:
            return False
        if not self.available:
            return False
        expiry_time = self.token_created_at + timedelta(minutes=self.expiration_time)
        is_valid = timezone.now() < expiry_time
        # Update available status based on expiration
        if not is_valid and self.available:
            self.available = False
            self.save(update_fields=['available'])
        return is_valid
    
    def regenerate_token(self):
        """Generate a new verification token (invalidates the old one first)"""
        # Step 1: Invalidate the current token for security
        self.available = False
        self.save(update_fields=['available'])
        
        # Step 2: Generate new token and make it available
        self.verification_token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.available = True
        self.save()


@receiver(post_save, sender=User)
def create_email_verification(sender, instance, created, **kwargs):
    """Automatically create EmailVerification when a User is created"""
    if created:
        EmailVerification.objects.create(user=instance)


class RobotOrder(models.Model):
    """Model to store robot call history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='robot_orders')
    robot_uuid = models.CharField(max_length=255)
    point_id = models.CharField(max_length=255)
    point_name = models.CharField(max_length=255, blank=True, null=True)
    status_code = models.IntegerField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'robot_orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.point_name or self.point_id} - {self.created_at}"
