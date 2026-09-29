from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Short code e.g. RND for Roads & Drainage")
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_staff_count(self):
        return self.staff_members.filter(user__is_active=True).count()

    @property
    def active_complaints_count(self):
        from complaints.models import Complaint
        return Complaint.objects.filter(
            department=self
        ).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()
