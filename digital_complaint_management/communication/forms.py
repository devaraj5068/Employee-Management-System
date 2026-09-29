from django import forms
from .models import ComplaintMessage

class ComplaintMessageForm(forms.ModelForm):
    class Meta:
        model = ComplaintMessage
        fields = ['message', 'attachment', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message, update, or clarification question here...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
