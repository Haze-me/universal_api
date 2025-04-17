
from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'db_type', 'target_table', 'verification_method', 'created_at')
    search_fields = ('name', 'db_type', 'target_table')
    readonly_fields = ('id', 'api_key', 'created_at', 'updated_at')
    fieldsets = (
        ('Company Information', {
            'fields': ('id', 'name', 'api_key', 'created_at', 'updated_at')
        }),
        ('Database Configuration', {
            'fields': ('db_type', 'connection_type', 'connection_string', 'db_host', 
                      'db_port', 'db_name', 'db_user', 'db_password', 'target_table')
        }),
        ('Verification Settings', {
            'fields': ('verification_method',)
        }),
        ('Validation Rules', {
            'fields': ('validation_rules',)
        }),
    )
