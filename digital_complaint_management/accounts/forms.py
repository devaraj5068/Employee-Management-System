from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password', 'class': 'form-control'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-control'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter desired username', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+91 9876543210', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'placeholder': 'Residential / Contact Address', 'rows': 3, 'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("A username is required.")
        username = username.strip()
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("An email address is required.")
        email = email.strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')

        if p1 and p2:
            if p1 != p2:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                validate_password(p1)
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data['email'].strip().lower()
        existing = CustomUser.objects.filter(email__iexact=email).first()
        if existing and not existing.is_verified:
            existing.username = self.cleaned_data['username']
            existing.first_name = self.cleaned_data['first_name']
            existing.last_name = self.cleaned_data['last_name']
            existing.phone_number = self.cleaned_data.get('phone_number', '')
            existing.address = self.cleaned_data.get('address', '')
            existing.set_password(self.cleaned_data['password'])
            existing.account_status = 'INACTIVE'
            if commit:
                existing.save()
            return existing

        user = super().save(commit=False)
        user.email = email
        user.set_password(self.cleaned_data['password'])
        user.role = 'CITIZEN'
        user.is_verified = False
        user.account_status = 'INACTIVE'
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-control'}),
        label="Username / Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'}),
        label="Password"
    )


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': '6-digit OTP', 'class': 'form-control text-center fs-4 letter-spacing'}),
        label="Enter OTP"
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email address', 'class': 'form-control'}),
        label="Registered Email"
    )


class ResetPasswordForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': '6-digit OTP received', 'class': 'form-control'}),
        label="Verification OTP"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'form-control'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'form-control'}),
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2:
            if p1 != p2:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                validate_password(p1)
        return cleaned_data
