
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class SMSService:
    """
    Service for sending SMS messages
    This is a generic implementation that can be adapted to work with various SMS providers
    like Twilio, Nexmo, AWS SNS, etc.
    """
    
    @staticmethod
    def send_sms(phone_number, message, provider=None):
        """
        Send an SMS message to a phone number
        
        Args:
            phone_number (str): The recipient's phone number
            message (str): The message to send
            provider (str, optional): The SMS provider to use. Defaults to None.
            
        Returns:
            dict: A dictionary with the result of the operation
        """
        # Get SMS provider settings
        if not provider:
            provider = getattr(settings, 'DEFAULT_SMS_PROVIDER', 'twilio')
        
        # Send SMS based on provider
        if provider == 'twilio':
            return SMSService.send_twilio_sms(phone_number, message)
        elif provider == 'nexmo':
            return SMSService.send_nexmo_sms(phone_number, message)
        elif provider == 'aws_sns':
            return SMSService.send_aws_sns_sms(phone_number, message)
        else:
            return {'success': False, 'error': f'Unsupported SMS provider: {provider}'}
    
    @staticmethod
    def send_twilio_sms(phone_number, message):
        """Send SMS using Twilio"""
        try:
            # Get Twilio credentials from settings
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
            
            if not all([account_sid, auth_token, from_number]):
                return {'success': False, 'error': 'Twilio credentials not configured'}
            
            # Import Twilio client
            try:
                from twilio.rest import Client
                client = Client(account_sid, auth_token)
            except ImportError:
                return {'success': False, 'error': 'Twilio package not installed. Run: pip install twilio'}
            
            # Send SMS
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            
            return {'success': True, 'message_id': message.sid}
        
        except Exception as e:
            logger.error(f"Error sending Twilio SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_nexmo_sms(phone_number, message):
        """Send SMS using Nexmo/Vonage"""
        try:
            # Get Nexmo credentials from settings
            api_key = getattr(settings, 'NEXMO_API_KEY', None)
            api_secret = getattr(settings, 'NEXMO_API_SECRET', None)
            from_name = getattr(settings, 'NEXMO_FROM_NAME', 'Verification')
            
            if not all([api_key, api_secret]):
                return {'success': False, 'error': 'Nexmo credentials not configured'}
            
            # Import Nexmo client
            try:
                import vonage
                client = vonage.Client(key=api_key, secret=api_secret)
                sms = vonage.Sms(client)
            except ImportError:
                return {'success': False, 'error': 'Vonage package not installed. Run: pip install vonage'}
            
            # Send SMS
            response = sms.send_message({
                'from': from_name,
                'to': phone_number,
                'text': message
            })
            
            if response['messages'][0]['status'] == '0':
                return {'success': True, 'message_id': response['messages'][0]['message-id']}
            else:
                return {'success': False, 'error': response['messages'][0]['error-text']}
        
        except Exception as e:
            logger.error(f"Error sending Nexmo SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_aws_sns_sms(phone_number, message):
        """Send SMS using AWS SNS"""
        try:
            # Import boto3
            try:
                import boto3
            except ImportError:
                return {'success': False, 'error': 'Boto3 package not installed. Run: pip install boto3'}
            
            # Create SNS client
            sns = boto3.client('sns')
            
            # Send SMS
            response = sns.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': getattr(settings, 'AWS_SNS_SENDER_ID', 'Verify')
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            return {'success': True, 'message_id': response['MessageId']}
        
        except Exception as e:
            logger.error(f"Error sending AWS SNS SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
