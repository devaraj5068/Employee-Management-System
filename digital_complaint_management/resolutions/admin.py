from django.contrib import admin
from .models import Resolution

@admin.register(Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'resolved_by', 'verification_status', 'verified_by', 'resolved_at')
    list_filter = ('verification_status', 'resolved_at')
    search_fields = ('complaint__complaint_id', 'description', 'remarks', 'resolved_by__username')
