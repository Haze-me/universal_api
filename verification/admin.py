
from django.contrib import admin
from .models import VerificationCode, SMSConfig, SMSTemplate, SMSLog

@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('company', 'email', 'phone', 'code', 'is_used', 'is_expired', 'created_at')
    search_fields = ('email', 'phone', 'code')
    list_filter = ('is_used', 'company')
    readonly_fields = ('id', 'created_at', 'expires_at')
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True

@admin.register(SMSConfig)
class SMSConfigAdmin(admin.ModelAdmin):
    list_display = ('company', 'provider', 'use_custom_sms')
    list_filter = ('provider', 'use_custom_sms')
    search_fields = ('company__name',)
    fieldsets = (
        ('Company Information', {
            'fields': ('company', 'provider', 'use_custom_sms')
        }),
        ('Twilio Settings', {
            'fields': ('twilio_account_sid', 'twilio_auth_token', 'twilio_from_number'),
            'classes': ('collapse',),
        }),
        ('Nexmo Settings', {
            'fields': ('nexmo_api_key', 'nexmo_api_secret', 'nexmo_from_name'),
            'classes': ('collapse',),
        }),
        ('AWS SNS Settings', {
            'fields': ('aws_access_key', 'aws_secret_key', 'aws_region', 'aws_sender_id'),
            'classes': ('collapse',),
        }),
    )

@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('company', 'template_type')
    list_filter = ('template_type',)
    search_fields = ('company__name', 'content')

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('company', 'template_type', 'recipient', 'status', 'sent_at')
    list_filter = ('status', 'template_type')
    search_fields = ('company__name', 'recipient', 'content')
    readonly_fields = ('company', 'template_type', 'recipient', 'content', 'status', 'error_message', 'sent_at')
