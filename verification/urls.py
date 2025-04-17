
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VerificationViewSet, VerifyCodeAPIView,
    SMSConfigViewSet, SMSTemplateViewSet
)

router = DefaultRouter()
router.register(r'codes', VerificationViewSet)
router.register(r'sms/config', SMSConfigViewSet)
router.register(r'sms/templates', SMSTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify-code'),
]
