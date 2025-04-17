from django.db import models
from companies.models import Company

class EmailConfig(models.Model):
    """Model for storing company-specific email configurations"""
    EMAIL_BACKEND_CHOICES = (
        ('smtp', 'SMTP Server'),
        ('sendgrid', 'SendGrid API'),
        ('mailgun', 'Mailgun API'),
        ('postmark', 'Postmark API'),
        ('ses', 'Amazon SES'),
        ('brevo', 'Brevo API'),
    )
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='email_config')
    
    # Email backend type
    backend_type = models.CharField(max_length=20, choices=EMAIL_BACKEND_CHOICES, default='smtp')
    
    # SMTP settings
    smtp_host = models.CharField(max_length=255, blank=True, null=True)
    smtp_port = models.IntegerField(blank=True, null=True)
    smtp_username = models.CharField(max_length=255, blank=True, null=True)
    smtp_password = models.CharField(max_length=255, blank=True, null=True)
    use_tls = models.BooleanField(default=True)
    
    # API-based settings
    api_key = models.CharField(max_length=255, blank=True, null=True, 
                              help_text="API key for SendGrid, Mailgun, Postmark, Brevo, etc.")
    domain = models.CharField(max_length=255, blank=True, null=True, 
                             help_text="Domain for Mailgun or region for Amazon SES")
    
    from_email = models.EmailField()
    
    # Whether to use custom or default email settings
    use_custom_email = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Email Config for {self.company.name}"

class EmailTemplate(models.Model):
    """Model for storing email templates for different purposes"""
    TEMPLATE_TYPES = (
        ('welcome', 'Welcome Email'),
        ('verification', 'Verification Code'),
        ('password_reset', 'Password Reset'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='email_templates')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text="Use {{placeholder}} syntax for dynamic content")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'template_type')
    
    def __str__(self):
        return f"{self.get_template_type_display()} for {self.company.name}"

class EmailLog(models.Model):
    """Model for logging email sending attempts"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='email_logs')
    template_type = models.CharField(max_length=20, choices=EmailTemplate.TEMPLATE_TYPES)
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20)  # success, failed
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Email to {self.recipient} ({self.status})"