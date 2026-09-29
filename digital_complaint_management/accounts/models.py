import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

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
    
    # Verification & Security
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=128, blank=True, null=True, help_text="Hashed 6-digit OTP")
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.IntegerField(default=0)
    otp_created_at = models.DateTimeField(blank=True, null=True)
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

    def generate_otp(self):
        """
        Generate a cryptographically secure 6-digit OTP valid for 10 minutes.
        Stores the hashed OTP securely and returns the plain 6-digit string
        solely for sending via email.
        """
        import secrets
        from django.contrib.auth.hashers import make_password

        plain_otp = str(secrets.randbelow(900000) + 100000)
        self.otp_code = make_password(plain_otp)
        self.otp_expiry = timezone.now() + timedelta(minutes=10)
        self.otp_created_at = timezone.now()
        self.otp_attempts = 0
        self.save(update_fields=['otp_code', 'otp_expiry', 'otp_created_at', 'otp_attempts'])
        return plain_otp

    def verify_otp(self, entered_otp):
        """
        Verify the entered OTP with attempt limits, expiry, and secure hash check.
        """
        from django.contrib.auth.hashers import check_password

        if not self.otp_code or not self.otp_expiry:
            return False, "No OTP requested. Please request a new verification code."

        if timezone.now() > self.otp_expiry:
            self.otp_code = None
            self.save(update_fields=['otp_code'])
            return False, "OTP has expired. Please request a new OTP."

        if self.otp_attempts >= 5:
            self.otp_code = None
            self.save(update_fields=['otp_code'])
            return False, "Maximum verification attempts (5) exceeded. This OTP is now invalid. Please request a new OTP."

        self.otp_attempts += 1
        self.save(update_fields=['otp_attempts'])

        entered_clean = str(entered_otp).strip()
        if check_password(entered_clean, self.otp_code):
            self.is_verified = True
            self.account_status = 'ACTIVE'
            self.is_active = True
            self.otp_code = None
            self.otp_expiry = None
            self.otp_attempts = 0
            self.save(update_fields=['is_verified', 'account_status', 'is_active', 'otp_code', 'otp_expiry', 'otp_attempts'])
            return True, "Account successfully verified and activated!"
        else:
            remaining = 5 - self.otp_attempts
            if remaining <= 0:
                self.otp_code = None
                self.save(update_fields=['otp_code'])
                return False, "Incorrect OTP. Maximum attempts exceeded. Please request a new OTP."
            return False, f"Invalid OTP code. {remaining} attempt(s) remaining."


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


class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ('REGISTRATION', 'Registration Verification'),
        ('LOGIN', 'Login Verification'),
        ('PASSWORD_RESET', 'Password Reset Verification'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otp_verifications',
        null=True,
        blank=True
    )
    email = models.EmailField(db_index=True)
    otp_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    last_sent_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.purpose} OTP for {self.email} ({'Verified' if self.is_verified else 'Pending'})"

    @classmethod
    def create_otp(cls, email, purpose, user=None):
        """
        Invalidates existing active OTPs for this email and purpose,
        enforces 30s cooldown and 5/hour rate limits,
        generates 6-digit OTP, hashes it, and stores OTPVerification.
        Returns (plain_otp: str, instance: OTPVerification).
        """
        import secrets
        from django.contrib.auth.hashers import make_password
        from django.core.exceptions import ValidationError

        email = email.strip().lower()
        now = timezone.now()

        # Check 60-second resend cooldown
        latest = cls.objects.filter(email=email, purpose=purpose).order_by('-created_at').first()
        if latest and latest.last_sent_at:
            elapsed = (now - latest.last_sent_at).total_seconds()
            if elapsed < 60:
                raise ValidationError(f"Please wait {int(60 - elapsed)} seconds before requesting another code.")

        # Check rate limit: 5 requests per hour
        one_hour_ago = now - timedelta(hours=1)
        hourly_count = cls.objects.filter(email=email, purpose=purpose, created_at__gte=one_hour_ago).count()
        if hourly_count >= 5:
            raise ValidationError("Maximum OTP requests exceeded (5 per hour). Please try again later.")

        # Invalidate previous pending OTPs
        cls.objects.filter(email=email, purpose=purpose, is_verified=False).update(
            expires_at=now
        )

        plain_otp = str(secrets.randbelow(900000) + 100000)
        otp_hash = make_password(plain_otp)
        expires_at = now + timedelta(minutes=5)

        instance = cls.objects.create(
            user=user,
            email=email,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
            attempts=0,
            is_verified=False,
            last_sent_at=now
        )
        return plain_otp, instance

    def verify(self, entered_otp):
        """
        Validates the entered OTP code against the stored hash.
        Checks single-use, 5-minute expiration, and 5-attempt limit.
        """
        from django.contrib.auth.hashers import check_password

        now = timezone.now()

        if self.is_verified:
            return False, "This OTP has already been used."

        if self.attempts >= 5:
            return False, "Too many incorrect attempts. Please request a new OTP."

        if now > self.expires_at:
            return False, "OTP has expired. Please request a new OTP."

        self.attempts += 1
        self.save(update_fields=['attempts'])

        entered_clean = str(entered_otp).strip()
        if check_password(entered_clean, self.otp_hash):
            self.is_verified = True
            self.used_at = now
            self.save(update_fields=['is_verified', 'used_at'])

            # If user attached and purpose is registration, activate account
            if self.user and self.purpose == 'REGISTRATION':
                self.user.is_verified = True
                self.user.account_status = 'ACTIVE'
                self.user.is_active = True
                self.user.save(update_fields=['is_verified', 'account_status', 'is_active'])

            return True, "Verification successful."
        else:
            remaining = 5 - self.attempts
            if remaining <= 0:
                self.expires_at = now
                self.save(update_fields=['expires_at'])
                return False, "Too many incorrect attempts. Please request a new OTP."
            return False, f"Invalid OTP. Please try again. ({remaining} attempt(s) remaining)"


class TemporaryRegistration(models.Model):
    """
    Holds pending Citizen registration details temporarily until OTP verification succeeds.
    No permanent CustomUser record is created until the 6-digit OTP is verified.
    """
    username = models.CharField(max_length=150, db_index=True)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Temporary Registration'
        verbose_name_plural = 'Temporary Registrations'
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Pending registration: {self.username} ({self.email})"


# Model alias for compliance with specifications
EmailOTP = OTPVerification


