from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Company
from .db_handlers import insert_data, find_user, update_user_password
from .validators import validate_data
from verification.models import VerificationCode
from email_service.utils import generate_verification_code, send_email
from verification.utils import generate_verification_code as generate_sms_code, send_sms
from django.utils import timezone
from .authentication import ApiKeyAuthentication
from .throttling import CompanyAnonRateThrottle, CompanyUserRateThrottle
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class UniversalSubmitAPIView(APIView):
    """
    Universal API endpoint for submitting form data
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CompanyAnonRateThrottle]
    
    def post(self, request):
        try:
            # Get company ID from request headers
            company_id = request.headers.get('X-Company-ID')
            if not company_id:
                return Response({"error": "X-Company-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find company by ID
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get form data
            data = request.data
            
            # Validate data against company-specific validation rules
            try:
                validate_data(data, company.get_validation_rules())
            except Exception as e:
                return Response({"error": "Validation failed", "details": e.detail if hasattr(e, 'detail') else str(e)}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Handle verification if required
            if company.verification_method != 'none':
                verification_field = 'email' if company.verification_method == 'email' else 'phone'
                
                if verification_field not in data:
                    return Response(
                        {"error": f"{verification_field.capitalize()} is required for verification"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Generate verification code
                code = generate_verification_code()
                
                # Create verification code record
                verification = VerificationCode.objects.create(
                    company=company,
                    **{verification_field: data[verification_field]},
                    code=code,
                    expires_at=timezone.now() + timezone.timedelta(hours=1)
                )
                
                # Send verification code
                if verification_field == 'email':
                    result = send_email(
                        company_id=company.id,
                        template_type='verification',
                        recipient=data[verification_field],
                        context={'code': code}
                    )
                else:  # phone verification
                    result = send_sms(
                        company_id=company.id,
                        template_type='verification',
                        phone_number=data[verification_field],
                        context={'code': code}
                    )
                    
                if not result['success']:
                    verification.delete()
                    return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    "message": f"Verification code sent to {data[verification_field]}",
                    "verification_id": verification.id,
                    "requires_verification": True
                })
            
            # Insert data into database
            try:
                inserted_id = insert_data(company, data)
                
                # Send welcome email if email is provided
                if 'email' in data:
                    send_email(
                        company_id=company.id,
                        template_type='welcome',
                        recipient=data['email'],
                        context=data
                    )
                
                # Send welcome SMS if phone is provided
                if 'phone' in data:
                    send_sms(
                        company_id=company.id,
                        template_type='welcome',
                        phone_number=data['phone'],
                        context=data
                    )
                
                return Response({
                    "success": True,
                    "message": "Data submitted successfully",
                    "id": inserted_id
                })
            
            except Exception as e:
                logger.error(f"Error in database operation: {str(e)}", exc_info=True)
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in submit API: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyAndSubmitAPIView(APIView):
    """
    API endpoint for verifying a code and submitting form data
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CompanyAnonRateThrottle]
    
    def post(self, request):
        try:
            # Get company ID from request headers
            company_id = request.headers.get('X-Company-ID')
            if not company_id:
                return Response({"error": "X-Company-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find company by ID
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get verification code and form data
            code = request.data.get('verification_code')
            data = request.data.get('data')
            
            if not code:
                return Response({"error": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not data:
                return Response({"error": "Form data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate data against company-specific validation rules
            try:
                validate_data(data, company.get_validation_rules())
            except Exception as e:
                return Response({"error": "Validation failed", "details": e.detail if hasattr(e, 'detail') else str(e)}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Determine verification field
            verification_field = 'email' if company.verification_method == 'email' else 'phone'
            
            if verification_field not in data:
                return Response(
                    {"error": f"{verification_field.capitalize()} is required for verification"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find the verification code
            query = {
                'company': company,
                'code': code,
                'is_used': False,
                verification_field: data[verification_field]
            }
            
            try:
                verification = VerificationCode.objects.get(**query)
                
                # Check if code is expired
                if verification.is_expired:
                    return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark code as used
                verification.is_used = True
                verification.save()
                
                # Insert data into database
                try:
                    inserted_id = insert_data(company, data)
                    
                    # Send welcome email if email is provided
                    if 'email' in data:
                        send_email(
                            company_id=company.id,
                            template_type='welcome',
                            recipient=data['email'],
                            context=data
                        )
                    
                    # Send welcome SMS if phone is provided
                    if 'phone' in data:
                        send_sms(
                            company_id=company.id,
                            template_type='welcome',
                            phone_number=data['phone'],
                            context=data
                        )
                    
                    return Response({
                        "success": True,
                        "message": "Data submitted successfully",
                        "id": inserted_id
                    })
                
                except Exception as e:
                    logger.error(f"Error in database operation: {str(e)}", exc_info=True)
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except VerificationCode.DoesNotExist:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in verify-submit API: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetRequestAPIView(APIView):
    """
    API endpoint for requesting a password reset
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CompanyAnonRateThrottle]
    
    def post(self, request):
        try:
            # Get company ID from request headers
            company_id = request.headers.get('X-Company-ID')
            if not company_id:
                return Response({"error": "X-Company-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find company by ID
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get identifier (email or phone)
            data = request.data
            
            # Determine verification field based on company settings
            verification_field = 'email' if company.verification_method == 'email' else 'phone'
            
            if verification_field not in data:
                return Response(
                    {"error": f"{verification_field.capitalize()} is required for password reset"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user exists
            user = find_user(company, {verification_field: data[verification_field]})
            if not user:
                return Response(
                    {"error": f"No user found with this {verification_field}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate verification code
            code = generate_verification_code()
            
            # Create verification code record
            verification = VerificationCode.objects.create(
                company=company,
                **{verification_field: data[verification_field]},
                code=code,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            # Send verification code
            if verification_field == 'email':
                result = send_email(
                    company_id=company.id,
                    template_type='password_reset',
                    recipient=data[verification_field],
                    context={'code': code}
                )
            else:  # phone verification
                result = send_sms(
                    company_id=company.id,
                    template_type='password_reset',
                    phone_number=data[verification_field],
                    context={'code': code}
                )
                
            if not result['success']:
                verification.delete()
                return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "message": f"Password reset code sent to {data[verification_field]}",
                "verification_id": verification.id
            })
        except Exception as e:
            logger.error(f"Unexpected error in password-reset-request API: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetVerifyAPIView(APIView):
    """
    API endpoint for verifying a password reset code and setting a new password
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CompanyAnonRateThrottle]
    
    def post(self, request):
        try:
            # Get company ID from request headers
            company_id = request.headers.get('X-Company-ID')
            if not company_id:
                return Response({"error": "X-Company-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find company by ID
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get verification code and new password
            data = request.data
            code = data.get('verification_code')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not code:
                return Response({"error": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not new_password:
                return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not confirm_password:
                return Response({"error": "Confirm password is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Determine verification field
            verification_field = 'email' if company.verification_method == 'email' else 'phone'
            
            if verification_field not in data:
                return Response(
                    {"error": f"{verification_field.capitalize()} is required for verification"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find the verification code
            query = {
                'company': company,
                'code': code,
                'is_used': False,
                verification_field: data[verification_field]
            }
            
            try:
                verification = VerificationCode.objects.get(**query)
                
                # Check if code is expired
                if verification.is_expired:
                    return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark code as used
                verification.is_used = True
                verification.save()
                
                # Find user and update password
                user = find_user(company, {verification_field: data[verification_field]})
                if not user:
                    return Response(
                        {"error": f"No user found with this {verification_field}"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Update user's password
                try:
                    update_user_password(company, user, new_password)
                    return Response({
                        "success": True,
                        "message": "Password updated successfully"
                    })
                except Exception as e:
                    logger.error(f"Error updating password: {str(e)}", exc_info=True)
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except VerificationCode.DoesNotExist:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in password-reset-verify API: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class ResendVerificationAPIView(APIView):
    """
    API endpoint for resending a verification code
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [CompanyAnonRateThrottle]
    
    def post(self, request):
        try:
            # Get company ID from request headers
            company_id = request.headers.get('X-Company-ID')
            if not company_id:
                return Response({"error": "X-Company-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Find company by ID
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get identifier (email or phone)
            data = request.data
            
            # Determine verification field based on company settings
            verification_field = 'email' if company.verification_method == 'email' else 'phone'
            
            if verification_field not in data:
                return Response(
                    {"error": f"{verification_field.capitalize()} is required for verification"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user exists in the database
            user = find_user(company, {verification_field: data[verification_field]})
            
            # If user doesn't exist in the database, check if there's a pending verification
            if not user:
                # Check if there's a pending verification for this email/phone
                pending_verification = VerificationCode.objects.filter(
                    company=company,
                    **{verification_field: data[verification_field]},
                    is_used=False
                ).exists()
                
                if not pending_verification:
                    return Response(
                        {"error": f"No pending registration found for this {verification_field}"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Invalidate any existing verification codes
            VerificationCode.objects.filter(
                company=company,
                **{verification_field: data[verification_field]},
                is_used=False
            ).update(is_used=True)
            
            # Generate new verification code
            code = generate_verification_code()
            
            # Create verification code record
            verification = VerificationCode.objects.create(
                company=company,
                **{verification_field: data[verification_field]},
                code=code,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            # Send verification code
            if verification_field == 'email':
                result = send_email(
                    company_id=company.id,
                    template_type='verification',
                    recipient=data[verification_field],
                    context={'code': code}
                )
            else:  # phone verification
                result = send_sms(
                    company_id=company.id,
                    template_type='verification',
                    phone_number=data[verification_field],
                    context={'code': code}
                )
                
            if not result['success']:
                verification.delete()
                return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "message": f"New verification code sent to {data[verification_field]}",
                "verification_id": verification.id
            })
            
        except Exception as e:
            logger.error(f"Unexpected error in resend-verification API: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)