from django.db import models
from django.conf import settings

NOTIFICATION_TYPES = (
    ('INFO', 'Information'),
    ('SUCCESS', 'Success'),
    ('WARNING', 'Warning'),
    ('URGENT', 'Urgent / Escalation'),
)

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='INFO')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.recipient.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"
