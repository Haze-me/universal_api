from django.core.mail.backends.base import BaseEmailBackend
import logging

logger = logging.getLogger(__name__)

class SESBackend(BaseEmailBackend):
    """
    Email backend for Amazon SES
    """
    
    def __init__(self, aws_access_key=None, aws_secret_key=None, aws_region=None, **kwargs):
        super().__init__(**kwargs)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        
        if not self.aws_access_key:
            from django.conf import settings
            self.aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        
        if not self.aws_secret_key:
            from django.conf import settings
            self.aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        
        if not self.aws_region:
            from django.conf import settings
            self.aws_region = getattr(settings, 'AWS_REGION', 'us-east-1')
    
    def send_messages(self, email_messages):
        """
        Send email messages via Amazon SES
        """
        if not self.aws_access_key or not self.aws_secret_key:
            logger.error("AWS credentials not configured")
            return 0
        
        try:
            import boto3
        except ImportError:
            logger.error("Boto3 package not installed. Run: pip install boto3")
            return 0
        
        # Create SES client
        ses = boto3.client(
            'ses',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        
        count = 0
        for message in email_messages:
            try:
                # Prepare data for SES API
                data = {
                    'Source': message.from_email,
                    'Destination': {
                        'ToAddresses': message.to,
                    },
                    'Message': {
                        'Subject': {
                            'Data': message.subject,
                        },
                        'Body': {
                            'Html': {
                                'Data': message.body,
                            }
                        }
                    }
                }
                
                if message.cc:
                    data['Destination']['CcAddresses'] = message.cc
                
                if message.bcc:
                    data['Destination']['BccAddresses'] = message.bcc
                
                # Send email
                response = ses.send_email(**data)
                
                if 'MessageId' in response:
                    count += 1
                else:
                    logger.error(f"Failed to send email via Amazon SES: {response}")
            
            except Exception as e:
                logger.error(f"Error sending email via Amazon SES: {str(e)}")
        
        return count
