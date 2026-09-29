from django import forms
from .models import Department
from accounts.models import CustomUser

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'head_of_department', 'contact_email', 'contact_phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short Code (e.g. ELEC)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Scope of jurisdiction/work'}),
            'head_of_department': forms.Select(attrs={'class': 'form-select'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'dept@civic.gov'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 0000000000'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow staff or admin to be selected as Head of Department
        self.fields['head_of_department'].queryset = CustomUser.objects.filter(role__in=['STAFF', 'ADMIN'])
