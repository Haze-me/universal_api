
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VerificationCode, SMSConfig, SMSTemplate
from .serializers import (
    VerificationCodeSerializer, VerifyCodeSerializer, 
    SMSConfigSerializer, SMSTemplateSerializer
)
from email_service.utils import generate_verification_code, send_email
from .utils import generate_verification_code as generate_sms_code, send_sms
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class VerificationViewSet(viewsets.ModelViewSet):
    queryset = VerificationCode.objects.all()
    serializer_class = VerificationCodeSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new verification code"""
        company_id = request.data.get('company_id')
        email = request.data.get('email')
        phone = request.data.get('phone')
        
        if not company_id:
            return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email and not phone:
            return Response({"error": "Either email or phone is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate verification code
        code = generate_verification_code()
        
        # Create verification code record
        verification = VerificationCode.objects.create(
            company_id=company_id,
            email=email,
            phone=phone,
            code=code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        # Send verification code
        if email:
            result = send_email(
                company_id=company_id,
                template_type='verification',
                recipient=email,
                context={'code': code}
            )
        elif phone:
            result = send_sms(
                company_id=company_id,
                template_type='verification',
                phone_number=phone,
                context={'code': code}
            )
            
        if not result['success']:
            verification.delete()
            return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "message": f"Verification code sent to {email or phone}",
            "id": verification.id
        })

class VerifyCodeAPIView(APIView):
    """API view for verifying a code"""
    
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            company_id = serializer.validated_data['company_id']
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            code = serializer.validated_data['code']
            
            # Find the verification code
            query = {
                'company_id': company_id,
                'code': code,
                'is_used': False,
            }
            
            if email:
                query['email'] = email
            elif phone:
                query['phone'] = phone
            
            try:
                verification = VerificationCode.objects.get(**query)
                
                # Check if code is expired
                if verification.is_expired:
                    return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark code as used
                verification.is_used = True
                verification.save()
                
                return Response({"success": True, "message": "Verification successful"})
            
            except VerificationCode.DoesNotExist:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SMSConfigViewSet(viewsets.ModelViewSet):
    queryset = SMSConfig.objects.all()
    serializer_class = SMSConfigSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the SMS provider connection"""
        config = self.get_object()
        phone = request.data.get('phone')
        
        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Send a test SMS
            result = send_sms(
                company_id=config.company.id,
                template_type='verification',
                phone_number=phone,
                context={'code': '123456'}  # Test code
            )
            
            if result['success']:
                return Response({"status": "success", "message": "SMS sent successfully"})
            return Response({"status": "error", "message": result['error']})
        except Exception as e:
            return Response({"status": "error", "message": str(e)})

class SMSTemplateViewSet(viewsets.ModelViewSet):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates by company if company_id is provided"""
        queryset = SMSTemplate.objects.all()
        company_id = self.request.query_params.get('company_id', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset
