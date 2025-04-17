from django.core.mail.backends.base import BaseEmailBackend
import logging
import requests

logger = logging.getLogger(__name__)

class MailgunBackend(BaseEmailBackend):
    """
    Email backend for Mailgun API
    """
    
    def __init__(self, api_key=None, domain=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.domain = domain
        
        if not self.api_key:
            from django.conf import settings
            self.api_key = getattr(settings, 'MAILGUN_API_KEY', None)
        
        if not self.domain:
            from django.conf import settings
            self.domain = getattr(settings, 'MAILGUN_DOMAIN', None)
    
    def send_messages(self, email_messages):
        """
        Send email messages via Mailgun API
        """
        if not self.api_key or not self.domain:
            logger.error("Mailgun API key or domain not configured")
            return 0
        
        count = 0
        for message in email_messages:
            try:
                # Prepare data for Mailgun API
                data = {
                    'from': message.from_email,
                    'subject': message.subject,
                    'html': message.body,
                }
                
                # Add recipients
                data['to'] = message.to
                
                if message.cc:
                    data['cc'] = message.cc
                
                if message.bcc:
                    data['bcc'] = message.bcc
                
                # Send email
                response = requests.post(
                    f"https://api.mailgun.net/v3/{self.domain}/messages",
                    auth=("api", self.api_key),
                    data=data
                )
                
                if response.status_code == 200:
                    count += 1
                else:
                    logger.error(f"Failed to send email via Mailgun: {response.text}")
            
            except Exception as e:
                logger.error(f"Error sending email via Mailgun: {str(e)}")
        
        return count
