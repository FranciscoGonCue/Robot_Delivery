from django.urls import path
from . import views, auth_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', auth_views.register, name='auth-register'),
    path('auth/login/', auth_views.login, name='auth-login'),
    path('auth/logout/', auth_views.logout, name='auth-logout'),
    path('auth/user/', auth_views.get_current_user, name='auth-current-user'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('auth/verify-email/', auth_views.verify_email, name='verify-email'),
    path('auth/resend-verification/', auth_views.resend_verification_email, name='resend-verification'),
    
    # Profile endpoints (protected)
    path('auth/profile/update/', auth_views.update_profile, name='update-profile'),
    path('auth/profile/change-password/', auth_views.change_password, name='change-password'),
    path('auth/profile/request-verification/', auth_views.request_email_verification, name='request-verification'),
    
    # Keenon configuration endpoints (protected)
    path('keenon/config/', views.get_keenon_config, name='get-keenon-config'),
    path('keenon/config/update/', views.update_keenon_config, name='update-keenon-config'),
    
    # Protected endpoints (require authentication)
    path('targets/', views.get_target_list, name='target-list'),
    path('robot/call/', views.call_robot_task, name='robot-call'),
    path('token/refresh/', views.refresh_token, name='refresh-token'),
    path('endpoints/', views.endpoint_list, name='endpoint-list'),
    path('endpoints/create/', views.endpoint_create, name='endpoint-create'),
    path('endpoints/<int:endpoint_id>/update/', views.endpoint_update, name='endpoint-update'),
    path('endpoints/<int:endpoint_id>/execute/', views.endpoint_execute, name='endpoint-execute'),
    
    # Robot endpoints
    path('robot/list/', views.get_robot_list, name='robot-list'),
    
    # Store endpoints
    path('store/list/', views.get_store_list, name='store-list'),
]
