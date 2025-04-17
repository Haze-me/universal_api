from django.contrib import admin
from .models import EmailConfig, EmailTemplate, EmailLog

class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ('company', 'backend_type', 'from_email', 'use_custom_email')
    search_fields = ('company__name', 'from_email')
    list_filter = ('backend_type', 'use_custom_email', 'use_tls')
    fieldsets = (
        ('Company Information', {
            'fields': ('company', 'use_custom_email', 'from_email')
        }),
        ('Email Backend', {
            'fields': ('backend_type',)
        }),
        ('SMTP Settings', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'use_tls'),
            'classes': ('collapse',),
            'description': 'Configure these settings if using SMTP server'
        }),
        ('API Settings', {
            'fields': ('api_key', 'domain'),
            'classes': ('collapse',),
            'description': 'Configure these settings if using API-based email service'
        }),
    )

admin.site.register(EmailConfig, EmailConfigAdmin)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('company', 'template_type', 'subject')
    list_filter = ('template_type',)
    search_fields = ('company__name', 'subject', 'body')

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('company', 'template_type', 'recipient', 'status', 'sent_at')
    list_filter = ('status', 'template_type')
    search_fields = ('company__name', 'recipient', 'subject')
    readonly_fields = ('company', 'template_type', 'recipient', 'subject', 'status', 'error_message', 'sent_at')
