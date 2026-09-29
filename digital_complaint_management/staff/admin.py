from django.contrib import admin
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation', 'max_active_capacity', 'is_available')
    list_filter = ('department', 'is_available', 'designation')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
