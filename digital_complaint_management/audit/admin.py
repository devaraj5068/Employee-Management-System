from django.contrib import admin
from .models import ActivityLog, SystemConfiguration

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'complaint', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address', 'complaint__complaint_id')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'complaint', 'created_at')

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description', 'updated_at')
    search_fields = ('key', 'value', 'description')
