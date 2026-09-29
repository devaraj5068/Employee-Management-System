from django.db import models
from django.conf import settings
from departments.models import Department

class StaffProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    designation = models.CharField(max_length=100, default='Field Officer')
    employee_id = models.CharField(max_length=50, unique=True)
    max_active_capacity = models.PositiveIntegerField(default=15)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'user__first_name']
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'

    def __str__(self):
        dept_name = self.department.name if self.department else "Unassigned"
        return f"{self.user.get_full_name() or self.user.username} - {self.designation} ({dept_name})"

    @property
    def current_active_complaints_count(self):
        from complaints.models import Complaint
        return Complaint.objects.filter(
            assigned_staff=self.user
        ).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()

    @property
    def workload_percentage(self):
        if self.max_active_capacity == 0:
            return 100
        count = self.current_active_complaints_count
        return min(100, int((count / self.max_active_capacity) * 100))

    @property
    def can_take_new_complaint(self):
        return self.is_available and (self.current_active_complaints_count < self.max_active_capacity)
