from django.core.mail.backends.base import BaseEmailBackend
import logging

logger = logging.getLogger(__name__)

class SendGridBackend(BaseEmailBackend):
    """
    Email backend for SendGrid API
    """
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        
        if not self.api_key:
            from django.conf import settings
            self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    
    def send_messages(self, email_messages):
        """
        Send email messages via SendGrid API
        """
        if not self.api_key:
            logger.error("SendGrid API key not configured")
            return 0
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
        except ImportError:
            logger.error("SendGrid package not installed. Run: pip install sendgrid")
            return 0
        
        sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        
        count = 0
        for message in email_messages:
            try:
                from_email = Email(message.from_email)
                
                # Handle multiple recipients
                for recipient in message.to:
                    to_email = To(recipient)
                    content = Content("text/html", message.body)
                    mail = Mail(from_email, to_email, message.subject, content)
                    
                    # Add CC recipients
                    for cc_recipient in message.cc:
                        mail.add_cc(Email(cc_recipient))
                    
                    # Add BCC recipients
                    for bcc_recipient in message.bcc:
                        mail.add_bcc(Email(bcc_recipient))
                    
                    # Send email
                    response = sg.client.mail.send.post(request_body=mail.get())
                    
                    if response.status_code in (200, 201, 202):
                        count += 1
                    else:
                        logger.error(f"Failed to send email via SendGrid: {response.body}")
            
            except Exception as e:
                logger.error(f"Error sending email via SendGrid: {str(e)}")
        
        return count
