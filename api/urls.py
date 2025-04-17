from django.urls import path
from .views import (
    UniversalSubmitAPIView, 
    VerifyAndSubmitAPIView,
    PasswordResetRequestAPIView,
    PasswordResetVerifyAPIView,
    ResendVerificationAPIView
)

urlpatterns = [
    path('submit/', UniversalSubmitAPIView.as_view(), name='universal-submit'),
    path('verify-submit/', VerifyAndSubmitAPIView.as_view(), name='verify-and-submit'),
    path('password-reset/request/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password-reset/verify/', PasswordResetVerifyAPIView.as_view(), name='password-reset-verify'),
    path('resend-verification/', ResendVerificationAPIView.as_view(), name='resend-verification'),
]