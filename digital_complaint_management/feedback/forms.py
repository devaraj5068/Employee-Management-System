from django import forms
from .models import ComplaintFeedback

class ComplaintFeedbackForm(forms.ModelForm):
    class Meta:
        model = ComplaintFeedback
        fields = ['rating', 'satisfaction_level', 'resolution_quality', 'comments']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select fs-5'}),
            'satisfaction_level': forms.Select(attrs={'class': 'form-select'}),
            'resolution_quality': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your experience with the resolution quality, officer response, and timeliness...'}),
        }
