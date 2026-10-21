from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    VerifyOTPView,
    ResetPasswordView,
    ForgotPasswordUIView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('refresh-token/', TokenRefreshView.as_view(), name='auth_refresh_token'),
    path('me/', UserProfileView.as_view(), name='auth_profile'),
    path('get-profile/', UserProfileView.as_view(), name='auth_get_profile'),
    path('update-profile/', UserProfileView.as_view(), name='auth_update_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('request-otp/', ForgotPasswordView.as_view(), name='auth_request_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='auth_verify_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),
    path('forgot-password/ui/', ForgotPasswordUIView.as_view(), name='auth_forgot_password_ui'),
]

