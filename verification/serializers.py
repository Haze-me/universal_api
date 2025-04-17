
from rest_framework import serializers
from .models import VerificationCode, SMSConfig, SMSTemplate

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['id', 'company', 'email', 'phone', 'code', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'code', 'created_at', 'expires_at']

class VerifyCodeSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField()
    
    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Either email or phone must be provided")
        return data

class SMSConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSConfig
        fields = [
            'id', 'company', 'provider', 'twilio_account_sid', 'twilio_auth_token', 
            'twilio_from_number', 'nexmo_api_key', 'nexmo_api_secret', 'nexmo_from_name',
            'aws_access_key', 'aws_secret_key', 'aws_region', 'aws_sender_id', 'use_custom_sms'
        ]
        extra_kwargs = {
            'twilio_auth_token': {'write_only': True},
            'aws_secret_key': {'write_only': True},
        }

class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = ['id', 'company', 'template_type', 'content']
