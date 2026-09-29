from django.contrib import admin
from .models import ComplaintFeedback

@admin.register(ComplaintFeedback)
class ComplaintFeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'user', 'rating', 'satisfaction_level', 'resolution_quality', 'created_at')
    list_filter = ('rating', 'satisfaction_level', 'resolution_quality', 'created_at')
    search_fields = ('complaint__complaint_id', 'user__username', 'comments')
