from django import forms
from .models import Resolution

class ResolutionSubmissionForm(forms.ModelForm):
    class Meta:
        model = Resolution
        fields = ['description', 'remarks', 'resolution_proof', 'resolution_document']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe in detail the repairs or steps taken to resolve the complaint...'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional recommendations, preventive maintenance or remarks...'}),
            'resolution_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'resolution_document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ResolutionVerificationForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[('APPROVE', 'Approve Resolution & Close Complaint'), ('REJECT', 'Reject Resolution & Reopen In-Progress Task')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Feedback or reason for decision...'}),
        required=True
    )


class ComplaintReopenForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Why are you reopening this complaint? Explain what was unresolved or recurring...'}),
        required=True,
        label="Reason for Reopening"
    )
