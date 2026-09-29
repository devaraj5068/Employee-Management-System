from django.contrib import admin
from .models import ComplaintMessage

@admin.register(ComplaintMessage)
class ComplaintMessageAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'sender', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('complaint__complaint_id', 'sender__username', 'message')
