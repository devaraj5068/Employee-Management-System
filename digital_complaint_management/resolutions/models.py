from django.db import models
from django.conf import settings
from complaints.models import Complaint

VERIFICATION_CHOICES = (
    ('PENDING', 'Pending Admin Verification'),
    ('APPROVED', 'Verified & Approved'),
    ('REJECTED', 'Rejected (Requires Re-work)'),
)

class Resolution(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='resolution')
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_resolutions'
    )
    description = models.TextField(help_text="Detailed explanation of work completed to resolve the issue.")
    remarks = models.TextField(blank=True, help_text="Operational remarks or maintenance recommendations.")
    resolution_proof = models.ImageField(upload_to='resolutions/images/%Y/%m/', blank=True, null=True, help_text="Proof photo after resolution")
    resolution_document = models.FileField(upload_to='resolutions/docs/%Y/%m/', blank=True, null=True, help_text="Work order, inspection sheet, or sign-off document")
    resolved_at = models.DateTimeField(auto_now_add=True)
    
    # Administrative Quality Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='APPROVED')
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_resolutions'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-resolved_at']
        verbose_name = 'Resolution'
        verbose_name_plural = 'Resolutions'

    def __str__(self):
        return f"Resolution for [{self.complaint.complaint_id}] by {self.resolved_by}"
