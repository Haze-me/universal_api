import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'universal_api.settings')
django.setup()

from email_service.utils import send_email
from companies.models import Company

# Replace with your company ID
COMPANY_ID = "b1ae5fa2-48f1-4b87-849b-039133158631"

def test_brevo_email():
    try:
        result = send_email(
            company_id=COMPANY_ID,
            template_type='verification',
            recipient='harrisonaka29@gmail.com',  # Use your email for testing
            context={'code': '123456'}
        )
        
        print(f"Email test result: {result}")
        return result
    except Exception as e:
        print(f"Error testing email: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    test_brevo_email()