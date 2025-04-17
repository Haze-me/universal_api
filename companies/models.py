
from django.db import models
import uuid
import json

class Company(models.Model):
    """Model for storing company information and database credentials"""
    DATABASE_TYPES = (
        ('mongodb', 'MongoDB'),
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
    )
    
    CONNECTION_TYPES = (
        ('params', 'Connection Parameters'),
        ('string', 'Connection String'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    api_key = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Database configuration
    db_type = models.CharField(max_length=20, choices=DATABASE_TYPES)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    connection_string = models.TextField(blank=True, null=True)
    db_host = models.CharField(max_length=255, blank=True, null=True)
    db_port = models.IntegerField(blank=True, null=True)
    db_name = models.CharField(max_length=255, blank=True, null=True)
    db_user = models.CharField(max_length=255, blank=True, null=True)
    db_password = models.CharField(max_length=255, blank=True, null=True)
    
    # Target table for user data
    target_table = models.CharField(max_length=255)
    
    # Verification method
    VERIFICATION_METHODS = (
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('none', 'No Verification'),
    )
    verification_method = models.CharField(
        max_length=10, 
        choices=VERIFICATION_METHODS,
        default='email'
    )
    
    # Custom validation rules (stored as JSON)
    validation_rules = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return self.name
    
    def get_validation_rules(self):
        """Returns the validation rules as a Python dictionary"""
        if isinstance(self.validation_rules, str):
            return json.loads(self.validation_rules)
        return self.validation_rules
