from django.contrib import admin
from .models import Endpoint, EmailVerification, UserKeenonConfig


@admin.register(UserKeenonConfig)
class UserKeenonConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'store_id', 'has_token', 'token_status', 'updated_at')
    search_fields = ('user__username', 'user__email', 'store_id')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Keenon Credentials', {
            'fields': ('client_id', 'client_secret', 'store_id', 'scene_code')
        }),
        ('Access Token', {
            'fields': ('access_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_token(self, obj):
        return '✅' if obj.access_token else '❌'
    has_token.short_description = 'Has Token'
    
    def token_status(self, obj):
        if not obj.access_token:
            return '❌ No token'
        elif obj.is_token_valid():
            return '✅ Valid'
        else:
            return '⚠️ Expired'
    token_status.short_description = 'Token Status'


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'method', 'path', 'created_at')
    search_fields = ('name', 'path', 'user__username')
    list_filter = ('method', 'created_at', 'user')
    readonly_fields = ('created_at',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'verification_status', 'token_created_at', 'verified_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('is_verified', 'token_created_at', 'verified_at')
    readonly_fields = ('verification_token', 'token_created_at', 'verified_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'verified_at')
        }),
        ('Token Information', {
            'fields': ('verification_token', 'token_created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_status(self, obj):
        if obj.is_verified:
            return '✅ Verified'
        elif obj.is_token_valid():
            return '⏳ Pending (Token Valid)'
        else:
            return '❌ Expired'
    
    verification_status.short_description = 'Status'
    
    actions = ['verify_users', 'regenerate_tokens']
    
    def verify_users(self, request, queryset):
        from django.utils import timezone
        count = 0
        for verification in queryset:
            if not verification.is_verified:
                verification.is_verified = True
                verification.verified_at = timezone.now()
                verification.save()
                count += 1
        
        self.message_user(request, f'{count} user(s) verified successfully.')
    
    verify_users.short_description = 'Verify selected users'
    
    def regenerate_tokens(self, request, queryset):
        count = 0
        for verification in queryset:
            if not verification.is_verified:
                verification.regenerate_token()
                count += 1
        
        self.message_user(request, f'Token regenerated for {count} user(s).')
    
    regenerate_tokens.short_description = 'Regenerate verification tokens'
