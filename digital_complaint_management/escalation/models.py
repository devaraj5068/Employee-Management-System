from django.db import models
from django.conf import settings
from complaints.models import Complaint, PRIORITY_CHOICES

ESCALATION_LEVELS = (
    (1, 'Level 1 - Field Staff'),
    (2, 'Level 2 - Department Head'),
    (3, 'Level 3 - System Administrator'),
    (4, 'Level 4 - Higher Civic Authority'),
)

class EscalationRule(models.Model):
    priority = models.CharField(max_length=20, unique=True, choices=PRIORITY_CHOICES)
    resolution_deadline_hours = models.PositiveIntegerField(help_text="Hours allowed before SLA breach")
    level1_warning_hours = models.PositiveIntegerField(default=12, help_text="Hours before deadline to issue warning alert")
    escalation_level_2_target = models.CharField(max_length=50, default='DEPARTMENT_HEAD')
    escalation_level_3_target = models.CharField(max_length=50, default='ADMINISTRATOR')
    escalation_level_4_target = models.CharField(max_length=50, default='HIGHER_AUTHORITY')

    class Meta:
        ordering = ['priority']
        verbose_name = 'SLA Escalation Rule'
        verbose_name_plural = 'SLA Escalation Rules'

    def __str__(self):
        return f"{self.get_priority_display()} SLA: {self.resolution_deadline_hours}h"


class EscalationLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='escalation_logs')
    level = models.PositiveSmallIntegerField(choices=ESCALATION_LEVELS, default=2)
    reason = models.TextField()
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_escalations'
    )
    is_automated = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-triggered_at']
        verbose_name = 'Escalation Log'
        verbose_name_plural = 'Escalation Logs'

    def __str__(self):
        return f"Level {self.level} Escalation on {self.complaint.complaint_id} ({self.triggered_at:%Y-%m-%d %H:%M})"
