from django.db import models
from django.conf import settings
from complaints.models import Complaint

RATING_CHOICES = (
    (5, '★★★★★ - Excellent (5/5)'),
    (4, '★★★★☆ - Good (4/5)'),
    (3, '★★★☆☆ - Average (3/5)'),
    (2, '★★☆☆☆ - Poor (2/5)'),
    (1, '★☆☆☆☆ - Very Poor (1/5)'),
)

SATISFACTION_CHOICES = (
    ('VERY_SATISFIED', 'Very Satisfied'),
    ('SATISFIED', 'Satisfied'),
    ('NEUTRAL', 'Neutral'),
    ('DISSATISFIED', 'Dissatisfied'),
    ('VERY_DISSATISFIED', 'Very Dissatisfied'),
)

QUALITY_CHOICES = (
    ('EXCELLENT', 'Excellent'),
    ('GOOD', 'Good'),
    ('AVERAGE', 'Average'),
    ('POOR', 'Poor'),
)

class ComplaintFeedback(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    satisfaction_level = models.CharField(max_length=30, choices=SATISFACTION_CHOICES, default='SATISFIED')
    resolution_quality = models.CharField(max_length=30, choices=QUALITY_CHOICES, default='GOOD')
    comments = models.TextField(blank=True, help_text="Feedback comments on resolution speed and officer conduct")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Citizen Feedback'
        verbose_name_plural = 'Citizen Feedbacks'

    def __str__(self):
        return f"Feedback for [{self.complaint.complaint_id}]: {self.rating}/5 stars"

    @property
    def stars_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
