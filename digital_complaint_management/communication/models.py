from django.db import models
from django.conf import settings
from complaints.models import Complaint

class ComplaintMessage(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='discussion_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_complaint_messages')
    message = models.TextField()
    attachment = models.FileField(upload_to='communication/%Y/%m/', blank=True, null=True)
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal staff note: hidden from citizen, visible only to Staff and Admin."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Complaint Message'
        verbose_name_plural = 'Complaint Messages'

    def __str__(self):
        flag = "[INTERNAL] " if self.is_internal else ""
        return f"{flag}{self.sender.username} on {self.complaint.complaint_id} ({self.created_at:%Y-%m-%d %H:%M})"
