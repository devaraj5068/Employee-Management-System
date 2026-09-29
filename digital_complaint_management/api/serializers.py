from rest_framework import serializers
from accounts.models import CustomUser
from departments.models import Department
from staff.models import StaffProfile
from complaints.models import Category, SubCategory, Complaint, ComplaintAttachment, ComplaintHistory
from feedback.models import ComplaintFeedback
from notifications.models import Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_verified']
        read_only_fields = ['id', 'role', 'is_verified']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'contact_email', 'contact_phone', 'is_active']


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'department', 'designation', 'employee_id', 'is_available', 'max_active_capacity']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'department', 'description', 'icon', 'default_priority', 'is_active', 'subcategories']


class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintAttachment
        fields = ['id', 'file', 'file_type', 'file_name', 'uploaded_at']


class ComplaintHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = ComplaintHistory
        fields = ['id', 'previous_status', 'new_status', 'changed_by_name', 'remarks', 'created_at']


class ComplaintSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    assigned_staff_name = serializers.CharField(source='assigned_staff.get_full_name', read_only=True, default='')
    attachments = ComplaintAttachmentSerializer(many=True, read_only=True)
    history_logs = ComplaintHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_id', 'title', 'description', 'category', 'category_name',
            'subcategory', 'priority', 'status', 'department', 'department_name',
            'assigned_staff', 'assigned_staff_name', 'location_address', 'latitude', 'longitude',
            'due_date', 'is_escalated', 'escalation_level', 'created_at', 'updated_at',
            'attachments', 'history_logs'
        ]
        read_only_fields = ['id', 'complaint_id', 'status', 'department', 'assigned_staff', 'due_date', 'is_escalated', 'escalation_level', 'created_at', 'updated_at']


class ComplaintFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintFeedback
        fields = ['id', 'complaint', 'rating', 'satisfaction_level', 'resolution_quality', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'link', 'notification_type', 'is_read', 'created_at']
