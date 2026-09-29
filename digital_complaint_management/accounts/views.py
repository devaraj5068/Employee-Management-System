import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.conf import settings

from datetime import timedelta
from django.contrib.auth.hashers import make_password

from .models import CustomUser, LoginHistory, OTPVerification, TemporaryRegistration
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    UserProfileUpdateForm, 
    OTPVerificationForm,
    ForgotPasswordForm,
    ResetPasswordForm
)
from .decorators import admin_required
from .email_utils import (
    send_registration_otp_email,
    send_registration_otp, 
    send_login_otp, 
    send_password_reset_otp, 
    is_email_configured
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Utility to obtain real client IP."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def mask_email(email):
    """
    Masks email address for display, e.g. cit****@gmail.com.
    Never exposes full email or OTP.
    """
    if not email or '@' not in email:
        return email or ''
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*' * 4
    elif len(local) <= 4:
        masked_local = local[:2] + '*' * 4
    else:
        masked_local = local[:3] + '*' * 4
    return f"{masked_local}@{domain}"


# ============================================================
# 1. USER REGISTRATION & EMAIL VERIFICATION OTP
# ============================================================

def register(request):
    """
    Handles first-time Citizen user registration.
    Validates form fields, checks for duplicate email and username,
    creates TemporaryRegistration (password hashed, CustomUser is NOT created yet),
    generates 6-digit OTP, and dispatches email via Gmail SMTP.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = (form.cleaned_data.get('username') or '').strip()
            first_name = (form.cleaned_data.get('first_name') or '').strip()
            last_name = (form.cleaned_data.get('last_name') or '').strip()
            email = (form.cleaned_data.get('email') or '').strip().lower()
            phone_number = (form.cleaned_data.get('phone_number') or '').strip()
            address = (form.cleaned_data.get('address') or '').strip()
            raw_password = form.cleaned_data.get('password')

            # Duplicate account checks against permanent CustomUser
            if CustomUser.objects.filter(email__iexact=email).exists():
                form.add_error('email', "An account with this email already exists.")
                return render(request, 'accounts/register.html', {'form': form})

            if CustomUser.objects.filter(username__iexact=username).exists():
                form.add_error('username', "A user with that username already exists.")
                return render(request, 'accounts/register.html', {'form': form})

            # Clean up any stale temporary registrations with this email or username
            TemporaryRegistration.objects.filter(
                Q(email__iexact=email) | Q(username__iexact=username)
            ).delete()

            # Store in TemporaryRegistration with hashed password (valid for 15 minutes)
            temp_reg = TemporaryRegistration.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                address=address,
                password_hash=make_password(raw_password),
                expires_at=timezone.now() + timedelta(minutes=15)
            )

            # Generate 6-digit OTP (5-minute validity, server-side generated & hashed)
            try:
                plain_otp, otp_obj = OTPVerification.create_otp(
                    email=email,
                    purpose='REGISTRATION',
                    user=None
                )
            except ValidationError as exc:
                temp_reg.delete()
                messages.error(request, str(exc))
                return render(request, 'accounts/register.html', {'form': form})

            # Send OTP via Gmail SMTP
            recipient_name = f"{temp_reg.first_name} {temp_reg.last_name}".strip() or temp_reg.username
            email_success, email_msg = send_registration_otp_email(email, recipient_name, plain_otp)

            if email_success:
                request.session['pending_registration_id'] = temp_reg.id
                request.session['verification_email'] = email
                request.session['verification_purpose'] = 'REGISTRATION'
                messages.success(request, "Verification code sent successfully to your email.")
                return redirect('accounts:verify_otp')
            else:
                # If email fails: DO NOT create Citizen account, delete temp registration and OTP
                temp_reg.delete()
                otp_obj.delete()
                logger.error("Failed to send registration OTP email to %s: %s", email, email_msg)
                messages.error(request, "Unable to send verification email. Please try again.")
                return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    """
    Verifies 6-digit Registration OTP entered by the Citizen.
    Upon successful verification:
      - Marks OTP as verified
      - Creates permanent Citizen account in MySQL CustomUser
      - Deletes TemporaryRegistration
      - Clears registration session
      - Redirects to existing Login page with success message
    """
    pending_id = request.session.get('pending_registration_id')
    email = request.session.get('verification_email')

    # Direct access check: must have pending registration session
    if not pending_id or not email:
        messages.warning(request, "Please complete registration first.")
        return redirect('accounts:register')

    # Retrieve pending registration
    temp_reg = TemporaryRegistration.objects.filter(id=pending_id, email__iexact=email).first()
    if not temp_reg or temp_reg.is_expired():
        if temp_reg:
            temp_reg.delete()
        request.session.pop('pending_registration_id', None)
        request.session.pop('verification_email', None)
        request.session.pop('verification_purpose', None)
        messages.error(request, "Registration session has expired. Please register again.")
        return redirect('accounts:register')

    # Retrieve active OTP
    latest_otp = OTPVerification.objects.filter(
        email=email,
        purpose='REGISTRATION'
    ).order_by('-created_at').first()

    # Calculate remaining cooldown seconds for Resend OTP button (60s cooldown)
    cooldown_remaining = 0
    if latest_otp and latest_otp.last_sent_at:
        elapsed = (timezone.now() - latest_otp.last_sent_at).total_seconds()
        if elapsed < 60:
            cooldown_remaining = int(60 - elapsed)

    if request.method == 'POST':
        entered_otp = (request.POST.get('otp') or request.POST.get('otp_code') or '').strip()
        if not entered_otp:
            messages.error(request, "Please enter the 6-digit verification code.")
            return render(request, 'accounts/verify_otp.html', {
                'masked_email': mask_email(email),
                'cooldown_remaining': cooldown_remaining,
            })

        if not latest_otp or latest_otp.is_verified:
            messages.error(request, "OTP has expired. Please request a new OTP.")
            return render(request, 'accounts/verify_otp.html', {
                'masked_email': mask_email(email),
                'cooldown_remaining': cooldown_remaining,
            })

        success, err_msg = latest_otp.verify(entered_otp)
        if success:
            # Check duplicate one last time before creating permanent CustomUser
            if CustomUser.objects.filter(email__iexact=temp_reg.email).exists():
                temp_reg.delete()
                request.session.pop('pending_registration_id', None)
                request.session.pop('verification_email', None)
                request.session.pop('verification_purpose', None)
                messages.info(request, "An account with this email already exists. Please log in.")
                return redirect('accounts:login')

            new_user = CustomUser(
                username=temp_reg.username,
                first_name=temp_reg.first_name,
                last_name=temp_reg.last_name,
                email=temp_reg.email,
                phone_number=temp_reg.phone_number,
                address=temp_reg.address,
                role='CITIZEN',
                is_verified=True,
                account_status='ACTIVE',
                is_active=True
            )
            new_user.password = temp_reg.password_hash
            new_user.save()

            # Associate OTP record with newly created permanent user
            latest_otp.user = new_user
            latest_otp.save(update_fields=['user'])

            # Clean up temporary registration & session
            temp_reg.delete()
            request.session.pop('pending_registration_id', None)
            request.session.pop('verification_email', None)
            request.session.pop('verification_purpose', None)

            messages.success(request, "Email verified successfully. Your Citizen account has been created.")
            return redirect('accounts:login')
        else:
            messages.error(request, err_msg or "Invalid OTP. Please try again.")

    context = {
        'masked_email': mask_email(email),
        'cooldown_remaining': cooldown_remaining,
    }
    return render(request, 'accounts/verify_otp.html', context)


# ============================================================
# 2. RESEND OTP (60s COOLDOWN, INVALIDATES PREVIOUS OTP)
# ============================================================

def resend_otp(request):
    """
    Handles OTP resend with server-side 60s cooldown.
    Generates new 6-digit OTP, invalidates previous OTP,
    sets 5-minute expiry, and dispatches via Gmail SMTP.
    """
    pending_id = request.session.get('pending_registration_id')
    email = request.session.get('verification_email')

    if not pending_id or not email:
        messages.warning(request, "Please complete registration first.")
        return redirect('accounts:register')

    temp_reg = TemporaryRegistration.objects.filter(id=pending_id, email__iexact=email).first()
    if not temp_reg or temp_reg.is_expired():
        if temp_reg:
            temp_reg.delete()
        request.session.pop('pending_registration_id', None)
        request.session.pop('verification_email', None)
        request.session.pop('verification_purpose', None)
        messages.error(request, "Registration session has expired. Please register again.")
        return redirect('accounts:register')

    # Create new OTP (checks 60s cooldown, invalidates old OTPs)
    try:
        plain_otp, otp_obj = OTPVerification.create_otp(
            email=email,
            purpose='REGISTRATION',
            user=None
        )
    except ValidationError as exc:
        messages.warning(request, str(exc))
        return redirect('accounts:verify_otp')

    recipient_name = f"{temp_reg.first_name} {temp_reg.last_name}".strip() or temp_reg.username
    email_success, email_msg = send_registration_otp_email(email, recipient_name, plain_otp)

    if email_success:
        messages.success(request, "Verification code sent successfully to your email.")
    else:
        messages.error(request, "Unable to send verification email. Please try again.")

    return redirect('accounts:verify_otp')


def redirect_by_role(user, next_url=None):
    """Redirects authenticated user to requested next URL or role-specific dashboard."""
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    if user.role == 'ADMIN' or user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    elif user.role == 'STAFF':
        return redirect('dashboard:staff_dashboard')
    else:
        return redirect('dashboard:user_dashboard')


def login_view(request):
    """
    Handles user authentication.
    Validates credentials, logs user in directly to Dashboard without OTP for existing users.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Lookup by username OR email
            user_obj = CustomUser.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            ).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    # Existing users in CustomUser table are authenticated directly
                    if not user.is_verified:
                        user.is_verified = True
                        user.account_status = 'ACTIVE'
                        user.save(update_fields=['is_verified', 'account_status'])

                    # Check account status
                    if user.account_status != 'ACTIVE':
                        messages.error(request, f"Your account is currently {user.account_status.lower()}. Please contact support.")
                        LoginHistory.objects.create(
                            user=user,
                            username_attempted=identifier,
                            ip_address=ip,
                            user_agent=user_agent,
                            status='FAILED',
                            failure_reason='Account suspended/inactive'
                        )
                        return render(request, 'accounts/login.html', {'form': form})

                    # Check if 2-Step Login OTP is enabled
                    enable_login_otp = getattr(settings, 'ENABLE_LOGIN_OTP', False)

                    if enable_login_otp:
                        try:
                            plain_otp, otp_obj = OTPVerification.create_otp(
                                email=user.email,
                                purpose='LOGIN',
                                user=user
                            )
                        except ValidationError as exc:
                            messages.warning(request, str(exc))
                            request.session['login_user_id'] = user.id
                            request.session['login_email'] = user.email
                            request.session['login_purpose'] = 'LOGIN'
                            return redirect('accounts:login_otp')

                        recipient_name = user.get_full_name() or user.username
                        email_success, email_msg = send_login_otp(user.email, recipient_name, plain_otp)

                        if email_success:
                            request.session['login_user_id'] = user.id
                            request.session['login_email'] = user.email
                            request.session['login_purpose'] = 'LOGIN'
                            messages.success(request, "Verification code sent successfully to your email.")
                            return redirect('accounts:login_otp')
                        else:
                            # In DEBUG mode, if SMTP credentials are placeholder or offline,
                            # fallback to direct login so administrators and field officers are never locked out
                            if getattr(settings, 'DEBUG', False):
                                logger.warning("Login OTP dispatch failed (%s). Falling back to direct login in DEBUG mode.", email_msg)
                                login(request, user)
                                LoginHistory.objects.create(
                                    user=user,
                                    username_attempted=user.username,
                                    ip_address=ip,
                                    user_agent=user_agent,
                                    status='SUCCESS'
                                )
                                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                                next_url = request.GET.get('next')
                                return redirect_by_role(user, next_url)
                            else:
                                messages.error(request, "Unable to send login verification email. Please try again.")
                                return render(request, 'accounts/login.html', {'form': form})
                    else:
                        # Standard Direct Login (Instant Authentication for Demo & Normal Users)
                        login(request, user)
                        LoginHistory.objects.create(
                            user=user,
                            username_attempted=user.username,
                            ip_address=ip,
                            user_agent=user_agent,
                            status='SUCCESS'
                        )
                        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                        next_url = request.GET.get('next')
                        return redirect_by_role(user, next_url)
                else:
                    LoginHistory.objects.create(
                        user=user_obj,
                        username_attempted=identifier,
                        ip_address=ip,
                        user_agent=user_agent,
                        status='FAILED',
                        failure_reason='Invalid password'
                    )
                    messages.error(request, "Invalid username/email or password.")
            else:
                messages.error(request, "No account found with those credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def login_otp_view(request):
    """
    Verifies 6-digit Login OTP, creates Django session, and redirects to dashboard.
    """
    user_id = request.session.get('login_user_id')
    email = request.session.get('login_email')

    if not user_id or not email:
        messages.warning(request, "No pending login session. Please sign in.")
        return redirect('accounts:login')

    user = get_object_or_404(CustomUser, id=user_id)

    # Calculate remaining cooldown seconds for resend
    cooldown_remaining = 0
    latest_otp = OTPVerification.objects.filter(
        email=email,
        purpose='LOGIN'
    ).order_by('-created_at').first()

    if latest_otp and latest_otp.last_sent_at:
        elapsed = (timezone.now() - latest_otp.last_sent_at).total_seconds()
        if elapsed < 30:
            cooldown_remaining = int(30 - elapsed)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        if not entered_otp:
            messages.error(request, "Please enter the 6-digit verification code.")
            return redirect('accounts:login_otp')

        if not latest_otp or latest_otp.is_verified:
            messages.error(request, "Verification code has expired. Please request a new code.")
            return redirect('accounts:login_otp')

        success, err_msg = latest_otp.verify(entered_otp)
        if success:
            login(request, user)
            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            LoginHistory.objects.create(
                user=user,
                username_attempted=user.username,
                ip_address=ip,
                user_agent=user_agent,
                status='SUCCESS'
            )

            # Clear login session data
            request.session.pop('login_user_id', None)
            request.session.pop('login_email', None)
            request.session.pop('login_purpose', None)

            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect_by_role(user)
        else:
            messages.error(request, err_msg or "Invalid verification code.")

    context = {
        'masked_email': mask_email(email),
        'cooldown_remaining': cooldown_remaining,
    }
    return render(request, 'accounts/login_otp.html', context)


def logout_view(request):
    """Logs out user and clears session."""
    logout(request)
    messages.info(request, "You have been safely signed out.")
    return redirect('accounts:login')


# ============================================================
# 4. FORGOT PASSWORD & PASSWORD RESET OTP
# ============================================================

def forgot_password_view(request):
    """
    Allows user to request password reset OTP sent to registered email.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = CustomUser.objects.filter(email__iexact=email).first()

            if user:
                try:
                    plain_otp, otp_obj = OTPVerification.create_otp(
                        email=user.email,
                        purpose='PASSWORD_RESET',
                        user=user
                    )
                except ValidationError as exc:
                    messages.warning(request, str(exc))
                    request.session['reset_email'] = user.email
                    request.session['reset_purpose'] = 'PASSWORD_RESET'
                    return redirect('accounts:password_reset_otp')

                recipient_name = user.get_full_name() or user.username
                email_success, email_msg = send_password_reset_otp(user.email, recipient_name, plain_otp)

                if email_success:
                    request.session['reset_email'] = user.email
                    request.session['reset_purpose'] = 'PASSWORD_RESET'
                    messages.success(request, "Verification code sent successfully to your email.")
                    return redirect('accounts:password_reset_otp')
                else:
                    messages.error(request, "Unable to send verification email. Please try again.")
            else:
                # Do not leak whether user exists; show friendly info
                messages.info(request, "If an account with that email exists, a verification code has been dispatched.")
                request.session['reset_email'] = email
                return redirect('accounts:password_reset_otp')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def password_reset_otp_view(request):
    """
    Verifies 6-digit Password Reset OTP and sets new password.
    """
    email = request.session.get('reset_email')
    if not email:
        messages.warning(request, "No active password reset request. Please initiate one.")
        return redirect('accounts:forgot_password')

    user = CustomUser.objects.filter(email__iexact=email).first()

    cooldown_remaining = 0
    latest_otp = OTPVerification.objects.filter(
        email=email,
        purpose='PASSWORD_RESET'
    ).order_by('-created_at').first()

    if latest_otp and latest_otp.last_sent_at:
        elapsed = (timezone.now() - latest_otp.last_sent_at).total_seconds()
        if elapsed < 30:
            cooldown_remaining = int(30 - elapsed)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not entered_otp:
            messages.error(request, "Please enter the 6-digit verification code.")
            return redirect('accounts:password_reset_otp')

        if not latest_otp or latest_otp.is_verified:
            messages.error(request, "Verification code has expired. Please request a new code.")
            return redirect('accounts:password_reset_otp')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'accounts/password_reset_otp.html', {
                'masked_email': mask_email(email),
                'cooldown_remaining': cooldown_remaining,
            })

        if len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters long.")
            return render(request, 'accounts/password_reset_otp.html', {
                'masked_email': mask_email(email),
                'cooldown_remaining': cooldown_remaining,
            })

        success, err_msg = latest_otp.verify(entered_otp)
        if success:
            if user:
                user.set_password(new_password)
                user.save()

            request.session.pop('reset_email', None)
            request.session.pop('reset_purpose', None)
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, err_msg or "Invalid verification code.")

    context = {
        'masked_email': mask_email(email),
        'cooldown_remaining': cooldown_remaining,
    }
    return render(request, 'accounts/password_reset_otp.html', context)


# ============================================================
# 5. USER PROFILE & HISTORY
# ============================================================

@login_required
def profile_view(request):
    user = request.user
    recent_logins = user.login_histories.all()[:5]
    return render(request, 'accounts/profile.html', {
        'user_obj': user,
        'recent_logins': recent_logins
    })


@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_pw = request.POST.get('old_password')
        new_pw = request.POST.get('new_password')
        confirm_pw = request.POST.get('confirm_password')

        if not request.user.check_password(old_pw):
            messages.error(request, "Current password is incorrect.")
        elif new_pw != confirm_pw:
            messages.error(request, "New passwords do not match.")
        elif len(new_pw) < 6:
            messages.error(request, "New password must be at least 6 characters long.")
        else:
            request.user.set_password(new_pw)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:profile')

    return render(request, 'accounts/change_password.html')


@login_required
def login_history_view(request):
    if request.user.role == 'ADMIN' or request.user.is_superuser:
        histories = LoginHistory.objects.all().select_related('user')[:100]
    else:
        histories = request.user.login_histories.all()[:50]

    return render(request, 'accounts/login_history.html', {'histories': histories})
