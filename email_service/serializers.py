
from rest_framework import serializers
from .models import EmailConfig, EmailTemplate

class EmailConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfig
        fields = [
            'id', 'company', 'backend_type', 'smtp_host', 'smtp_port', 
            'smtp_username', 'smtp_password', 'use_tls', 'api_key', 
            'domain', 'from_email', 'use_custom_email'
        ]
        extra_kwargs = {
            'smtp_password': {'write_only': True},
            'api_key': {'write_only': True},
        }

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'company', 'template_type', 'subject', 'body']
