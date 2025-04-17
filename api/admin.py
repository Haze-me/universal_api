
from django.contrib import admin
from .models import ApiLog

@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'endpoint', 'method', 'status_code', 'ip_address', 'created_at')
    list_filter = ('method', 'status_code')
    search_fields = ('company_id', 'endpoint', 'ip_address')
    readonly_fields = ('company_id', 'endpoint', 'method', 'request_data', 'response_data', 'status_code', 'ip_address', 'user_agent', 'created_at')
