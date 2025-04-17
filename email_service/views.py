
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import EmailConfig, EmailTemplate
from .serializers import EmailConfigSerializer, EmailTemplateSerializer
from .utils import test_email_connection
from rest_framework.permissions import IsAuthenticated

class EmailConfigViewSet(viewsets.ModelViewSet):
    queryset = EmailConfig.objects.all()
    serializer_class = EmailConfigSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test the email connection"""
        config = self.get_object()
        
        try:
            result = test_email_connection(config)
            if result['success']:
                return Response({"status": "success", "message": "Email connection successful"})
            return Response({"status": "error", "message": result['error']})
        except Exception as e:
            return Response({"status": "error", "message": str(e)})

class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates by company if company_id is provided"""
        queryset = EmailTemplate.objects.all()
        company_id = self.request.query_params.get('company_id', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset
