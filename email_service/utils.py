import smtplib
from django.core.mail import EmailMessage
import string
import random
from .models import EmailTemplate, EmailLog
import logging

logger = logging.getLogger(__name__)

def get_email_backend(config=None):
    """Get an email backend using either custom or default settings"""
    from django.core.mail import get_connection
    
    if config and config.use_custom_email:
        if config.backend_type == 'smtp':
            # Use SMTP backend
            return get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=config.smtp_host,
                port=config.smtp_port,
                username=config.smtp_username,
                password=config.smtp_password,
                use_tls=config.use_tls,
            )
        elif config.backend_type == 'sendgrid':
            # Use SendGrid backend
            return get_connection(
                backend='email_service.backends.sendgrid_backend.SendGridBackend',
                api_key=config.api_key,
            )
        elif config.backend_type == 'mailgun':
            # Use Mailgun backend
            return get_connection(
                backend='email_service.backends.mailgun_backend.MailgunBackend',
                api_key=config.api_key,
                domain=config.domain,
            )
        elif config.backend_type == 'postmark':
            # Use Postmark backend
            return get_connection(
                backend='email_service.backends.postmark_backend.PostmarkBackend',
                api_key=config.api_key,
            )
        elif config.backend_type == 'ses':
            # Use Amazon SES backend
            return get_connection(
                backend='email_service.backends.ses_backend.SESBackend',
                aws_access_key=config.api_key,
                aws_secret_key=config.domain,  # Using domain field to store AWS secret key
                aws_region=config.smtp_host,  # Using smtp_host field to store AWS region
            )
        elif config.backend_type == 'brevo':
            # Use Brevo backend
            return get_connection(
                backend='email_service.backends.brevo_backend.BrevoBackend',
                api_key=config.api_key,
            )
    
    # Use default backend from settings
    return get_connection()

def test_email_connection(config):
    """Test email connection with the provided configuration"""
    if config.backend_type == 'smtp':
        # Test SMTP connection
        try:
            server = smtplib.SMTP(config.smtp_host, config.smtp_port)
            if config.use_tls:
                server.starttls()
            server.login(config.smtp_username, config.smtp_password)
            server.quit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    else:
        # Test API-based connection by sending a test email
        try:
            # Create a test email
            email = EmailMessage(
                subject='Test Email',
                body='This is a test email to verify your email configuration.',
                from_email=config.from_email,
                to=[config.from_email],  # Send to self
                connection=get_email_backend(config)
            )
            
            # Send the email
            sent = email.send(fail_silently=False)
            
            if sent:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Failed to send test email'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

def get_template_for_company(company_id, template_type):
    """Get the email template for a company, or use default if not found"""
    try:
        template = EmailTemplate.objects.get(company_id=company_id, template_type=template_type)
        return {
            'subject': template.subject,
            'body': template.body
        }
    except EmailTemplate.DoesNotExist:
        # Return default template
        return {
            'welcome': {
                'subject': 'Welcome to our service!',
                'body': 'Hello {{name}},\n\nWelcome to our service! We are excited to have you on board.\n\nBest regards,\nThe Team'
            },
            'verification': {
                'subject': 'Verify your account',
                'body': 'Hello,\n\nYour verification code is: {{code}}\n\nThis code will expire in 10 minutes.\n\nBest regards,\nThe Team'
            },
            'password_reset': {
                'subject': 'Reset your password',
                'body': 'Hello,\n\nYou requested a password reset. Your code is: {{code}}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nThe Team'
            }
        }.get(template_type)

def render_template(template, context):
    """Render an email template by replacing placeholders with actual values"""
    subject = template['subject']
    body = template['body']
    
    # Replace placeholders in subject and body
    for key, value in context.items():
        placeholder = '{{' + key + '}}'
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    return subject, body

def send_email(company_id, template_type, recipient, context):
    """Send an email using the company's template and email settings"""
    from companies.models import Company
    
    try:
        company = Company.objects.get(id=company_id)
        
        # Get email template
        template = get_template_for_company(company_id, template_type)
        
        # Render template with context
        subject, body = render_template(template, context)
        
        # Get email configuration
        try:
            email_config = company.email_config
        except:
            email_config = None
        
        # Get sender email
        from_email = email_config.from_email if email_config and email_config.use_custom_email else None
        
        if not from_email:
            from django.conf import settings
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[recipient],
            connection=get_email_backend(email_config)
        )
        
        # Send email
        email.send(fail_silently=False)
        
        # Log success
        EmailLog.objects.create(
            company=company,
            template_type=template_type,
            recipient=recipient,
            subject=subject,
            status='success'
        )
        
        return {'success': True}
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        
        # Log failure
        try:
            EmailLog.objects.create(
                company=company,
                template_type=template_type,
                recipient=recipient,
                subject=subject if 'subject' in locals() else '',
                status='failed',
                error_message=str(e)
            )
        except:
            pass
        
        return {'success': False, 'error': str(e)}

def generate_verification_code():
    """Generate a 6-digit alphanumeric verification code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))