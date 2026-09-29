from django.db import models
from django.conf import settings
from complaints.models import Complaint

ACTION_CHOICES = (
    ('CREATE', 'Created Complaint'),
    ('UPDATE', 'Updated Record'),
    ('ASSIGN', 'Assigned / Reassigned'),
    ('STATUS_CHANGE', 'Status Change'),
    ('RESOLVE', 'Submitted Resolution'),
    ('REOPEN', 'Reopened Complaint'),
    ('ESCALATE', 'Escalated Complaint'),
    ('DELETE', 'Deleted Resource'),
    ('LOGIN', 'User Login'),
    ('CONFIG_CHANGE', 'Configuration Change'),
)

class ActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} [{self.get_action_display()}] at {self.created_at:%Y-%m-%d %H:%M}"


class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'

    def __str__(self):
        return f"{self.key} = {self.value[:30]}"
