import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from departments.models import Department

PRIORITY_CHOICES = (
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
)

STATUS_CHOICES = (
    ('SUBMITTED', 'Submitted'),
    ('UNDER_REVIEW', 'Under Review'),
    ('ASSIGNED', 'Assigned'),
    ('IN_PROGRESS', 'In Progress'),
    ('ON_HOLD', 'On Hold'),
    ('RESOLVED', 'Resolved'),
    ('REJECTED', 'Rejected'),
    ('CLOSED', 'Closed'),
    ('REOPENED', 'Reopened'),
)

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='categories')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-tag', help_text='Bootstrap icon name e.g. bi-cone-striped, bi-lightning-charge')
    default_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Complaint Category'
        verbose_name_plural = 'Complaint Categories'

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    @property
    def total_complaints(self):
        return self.complaints.count()


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('category', 'name')
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Complaint(models.Model):
    complaint_id = models.CharField(max_length=30, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='complaints')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM', db_index=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED', db_index=True)
    
    # Assignment & Department
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='complaints', null=True, blank=True)
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    # Location Information
    location_address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Timelines & SLAs
    due_date = models.DateTimeField(null=True, blank=True, db_index=True)
    is_escalated = models.BooleanField(default=False, db_index=True)
    escalation_level = models.PositiveSmallIntegerField(default=1)
    escalation_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        indexes = [
            models.Index(fields=['complaint_id']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['department', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.complaint_id}] {self.title} ({self.get_status_display()})"

    @classmethod
    def generate_complaint_id(cls):
        """Generates consecutive ID in format RN-YYYY-XXXXXX."""
        current_year = timezone.now().year
        prefix = f"RN-{current_year}-"
        last_complaint = cls.objects.filter(complaint_id__startswith=prefix).order_by('-complaint_id').first()
        if last_complaint:
            try:
                last_number = int(last_complaint.complaint_id.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        return f"{prefix}{new_number:06d}"

    @property
    def is_overdue(self):
        if self.status in ['RESOLVED', 'CLOSED', 'REJECTED']:
            return False
        if self.due_date and timezone.now() > self.due_date:
            return True
        return False

    @property
    def progress_percentage(self):
        mapping = {
            'SUBMITTED': 15,
            'UNDER_REVIEW': 30,
            'ASSIGNED': 45,
            'IN_PROGRESS': 65,
            'ON_HOLD': 65,
            'RESOLVED': 90,
            'CLOSED': 100,
            'REJECTED': 100,
            'REOPENED': 40,
        }
        return mapping.get(self.status, 0)

    @property
    def priority_badge_class(self):
        classes = {
            'LOW': 'bg-success',
            'MEDIUM': 'bg-info text-dark',
            'HIGH': 'bg-warning text-dark',
            'CRITICAL': 'bg-danger text-white pulse-badge',
        }
        return classes.get(self.priority, 'bg-secondary')

    @property
    def status_badge_class(self):
        classes = {
            'SUBMITTED': 'bg-primary text-white',
            'UNDER_REVIEW': 'bg-secondary text-white',
            'ASSIGNED': 'bg-info text-dark',
            'IN_PROGRESS': 'bg-warning text-dark',
            'ON_HOLD': 'bg-dark text-white',
            'RESOLVED': 'bg-success text-white',
            'REJECTED': 'bg-danger text-white',
            'CLOSED': 'bg-secondary text-white',
            'REOPENED': 'bg-danger text-white',
        }
        return classes.get(self.status, 'bg-secondary')


def complaint_file_upload_to(instance, filename):
    return f"complaints/{timezone.now().strftime('%Y/%m')}/{instance.complaint.complaint_id}_{filename}"


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=complaint_file_upload_to)
    file_type = models.CharField(max_length=50, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Attachment {self.file_name or self.file.name} for {self.complaint.complaint_id}"

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = os.path.basename(self.file.name)
        
        # Determine file type
        ext = os.path.splitext(self.file_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.webp']:
            self.file_type = 'IMAGE'
        elif ext in ['.pdf', '.doc', '.docx', '.txt']:
            self.file_type = 'DOCUMENT'
        elif ext in ['.mp4', '.mov', '.avi']:
            self.file_type = 'VIDEO'
        else:
            self.file_type = 'OTHER'
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.file_type == 'IMAGE'

    @property
    def is_video(self):
        return self.file_type == 'VIDEO'


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history_logs')
    previous_status = models.CharField(max_length=30, blank=True, null=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaint_status_changes'
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Complaint History'
        verbose_name_plural = 'Complaint Histories'

    def __str__(self):
        return f"{self.complaint.complaint_id}: {self.previous_status} → {self.new_status} at {self.created_at:%Y-%m-%d %H:%M}"
