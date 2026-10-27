from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('CITIZEN', 'Citizen / Public User'),
        ('STAFF', 'Staff / Field Officer'),
        ('ADMIN', 'Administrator'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITIZEN', db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Account status & verified flag (citizens automatically verified upon registration)
    is_verified = models.BooleanField(default=True)
    account_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name or self.username} ({self.get_role_display()})"

    def is_citizen(self):
        return self.role == 'CITIZEN'

    def is_staff_member(self):
        return self.role in ['STAFF', 'ADMIN']

    def is_administrator(self):
        return self.role == 'ADMIN' or self.is_superuser


class LoginHistory(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='login_histories',
        null=True, 
        blank=True
    )
    username_attempted = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    failure_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username_attempted} - {self.status} at {self.timestamp:%Y-%m-%d %H:%M}"
