from django.core.mail.backends.base import BaseEmailBackend
import logging
import requests
import json

logger = logging.getLogger(__name__)

class BrevoBackend(BaseEmailBackend):
    """
    Email backend for Brevo (formerly Sendinblue) API
    """
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        
        if not self.api_key:
            from django.conf import settings
            self.api_key = getattr(settings, 'BREVO_API_KEY', None)
    
    def send_messages(self, email_messages):
        """
        Send email messages via Brevo API
        """
        if not self.api_key:
            logger.error("Brevo API key not configured")
            return 0
        
        count = 0
        for message in email_messages:
            try:
                # Prepare data for Brevo API
                data = {
                    "sender": {
                        "email": message.from_email,
                        "name": message.from_email.split('@')[0]  # Use part before @ as name
                    },
                    "to": [{"email": recipient} for recipient in message.to],
                    "subject": message.subject,
                    "htmlContent": message.body
                }
                
                # Add CC recipients if any
                if message.cc:
                    data["cc"] = [{"email": recipient} for recipient in message.cc]
                
                # Add BCC recipients if any
                if message.bcc:
                    data["bcc"] = [{"email": recipient} for recipient in message.bcc]
                
                # Send email
                response = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "api-key": self.api_key
                    },
                    data=json.dumps(data)
                )
                
                if response.status_code in (200, 201, 202):
                    count += 1
                    logger.info(f"Email sent successfully via Brevo: {response.json()}")
                else:
                    logger.error(f"Failed to send email via Brevo: {response.text}")
            
            except Exception as e:
                logger.error(f"Error sending email via Brevo: {str(e)}")
        
        return count