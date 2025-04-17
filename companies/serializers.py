from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'api_key', 'db_type', 'connection_type', 
            'connection_string', 'db_host', 'db_port', 'db_name', 
            'db_user', 'db_password', 'target_table', 
            'verification_method', 'validation_rules'
        ]
        read_only_fields = ['id', 'api_key']
        extra_kwargs = {
            'db_password': {'write_only': True},
            'connection_string': {'write_only': True},
        }
