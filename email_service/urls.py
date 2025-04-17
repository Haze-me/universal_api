from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailConfigViewSet, EmailTemplateViewSet

router = DefaultRouter()
router.register(r'config', EmailConfigViewSet)
router.register(r'templates', EmailTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
