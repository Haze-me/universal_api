
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('companies/', include('companies.urls')),
    path('email/', include('email_service.urls')),
    path('verification/', include('verification.urls')),
]
