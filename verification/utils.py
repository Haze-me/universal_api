
import string
import random
from .models import SMSTemplate, SMSLog
from .sms_service import SMSService

def generate_verification_code():
    """Generate a 6-digit alphanumeric verification code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

def get_sms_template_for_company(company_id, template_type):
    """Get the SMS template for a company, or use default if not found"""
    try:
        return SMSTemplate.objects.get(company_id=company_id, template_type=template_type)
    except SMSTemplate.DoesNotExist:
        # Return default template
        return {
            'welcome': {
                'content': 'Welcome to our service! We are excited to have you on board.'
            },
            'verification': {
                'content': 'Your verification code is: {{code}}. This code will expire in 10 minutes.'
            },
            'password_reset': {
                'content': 'You requested a password reset. Your code is: {{code}}. If you did not request this, please ignore this message.'
            }
        }.get(template_type)

def render_sms_template(template, context):
    """Render an SMS template by replacing placeholders with actual values"""
    content = template['content']
    
    # Replace placeholders in content
    for key, value in context.items():
        placeholder = '{{' + key + '}}'
        content = content.replace(placeholder, str(value))
    
    return content

def send_sms(company_id, template_type, phone_number, context):
    """Send an SMS using the company's template and SMS provider"""
    from companies.models import Company
    
    try:
        company = Company.objects.get(id=company_id)
        
        # Get SMS template
        template = get_sms_template_for_company(company_id, template_type)
        
        # Render template with context
        content = render_sms_template(template, context)
        
        # Get SMS configuration
        try:
            sms_config = company.sms_config
            provider = sms_config.provider if sms_config.use_custom_sms else None
        except:
            sms_config = None
            provider = None
        
        # Send SMS
        result = SMSService.send_sms(phone_number, content, provider)
        
        # Log result
        SMSLog.objects.create(
            company=company,
            template_type=template_type,
            recipient=phone_number,
            content=content,
            status='success' if result['success'] else 'failed',
            error_message=result.get('error', None)
        )
        
        return result
    
    except Exception as e:
        # Log failure
        try:
            SMSLog.objects.create(
                company=company,
                template_type=template_type,
                recipient=phone_number,
                content=content if 'content' in locals() else '',
                status='failed',
                error_message=str(e)
            )
        except:
            pass
        
        return {'success': False, 'error': str(e)}
