from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer
from rest_framework.permissions import IsAuthenticated

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        """Test the database connection for a company"""
        company = self.get_object()
        from api.db_handlers import get_db_connection
        
        try:
            conn = get_db_connection(company)
            if conn:
                return Response({"status": "success", "message": "Connection successful"})
            return Response({"status": "error", "message": "Could not establish connection"})
        except Exception as e:
            return Response({"status": "error", "message": str(e)})
