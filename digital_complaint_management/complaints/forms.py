from django import forms
from .models import Complaint, Category, SubCategory, ComplaintAttachment, PRIORITY_CHOICES, STATUS_CHOICES
from departments.models import Department
from accounts.models import CustomUser

class ComplaintRegistrationForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'title', 
            'category', 
            'subcategory', 
            'priority', 
            'description', 
            'location_address', 
            'latitude', 
            'longitude'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the issue (e.g. Broken Water Pipe on 5th Cross)'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'subcategory': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategory'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide complete, specific details about the issue, impact, and exact location markers...'}),
            'location_address': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_location_address', 'placeholder': 'Street, Area, Landmark, City'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        if 'category' in self.data:
            try:
                cat_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=cat_id, is_active=True)
            except (ValueError, TypeError):
                self.fields['subcategory'].queryset = SubCategory.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.filter(is_active=True)
        else:
            self.fields['subcategory'].queryset = SubCategory.objects.none()


class ComplaintStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason or operational remarks for this status transition...'}),
        required=True
    )


class ComplaintAssignmentForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_assign_dept'})
    )
    assigned_staff = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role__in=['STAFF', 'ADMIN']),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_assign_staff'})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Assignment notes or instructions for officer...'}),
        required=False
    )


class ComplaintPriorityUpdateForm(forms.Form):
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for re-prioritization...'}),
        required=True
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'department', 'description', 'icon', 'default_priority', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sanitation & Waste'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-trash'}),
            'default_priority': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
