from django.contrib import admin
from .models import Category, SubCategory, Complaint, ComplaintAttachment, ComplaintHistory

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'default_priority', 'icon', 'is_active')
    list_filter = ('department', 'is_active', 'default_priority')
    search_fields = ('name', 'description')
    inlines = [SubCategoryInline]

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')

class AttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ('file_type', 'file_name', 'uploaded_at')

class HistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'remarks', 'created_at')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'category', 'priority', 'status', 'department', 'assigned_staff', 'user', 'created_at', 'is_escalated')
    list_filter = ('status', 'priority', 'department', 'category', 'is_escalated', 'created_at')
    search_fields = ('complaint_id', 'title', 'description', 'user__username', 'location_address')
    readonly_fields = ('complaint_id', 'created_at', 'updated_at')
    inlines = [AttachmentInline, HistoryInline]
    ordering = ('-created_at',)
