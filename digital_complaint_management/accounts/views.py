import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from .models import CustomUser, LoginHistory
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    UserProfileUpdateForm, 
    ForgotPasswordForm,
    SetNewPasswordForm
)
from .decorators import admin_required
from .email_utils import send_password_reset_link_email

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Utility to obtain real client IP."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


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


# ============================================================
# 1. CITIZEN REGISTRATION (DIRECT, NO OTP, NO EMAIL VERIFY)
# ============================================================

def register(request):
    """
    Handles Citizen user registration directly:
    1. Citizen opens registration page.
    2. Enters required details.
    3. Django validates form and duplicate username/email.
    4. Account is created active and password hashed.
    5. Success message shown and redirected to Login page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                "Registration successful! Your Citizen account has been created. Please sign in."
            )
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ============================================================
# 2. USER LOGIN & LOGOUT (DIRECT, NO OTP)
# ============================================================

def login_view(request):
    """
    Handles user authentication for Citizens, Staff, and Admins:
    - Authenticates using username or email and password.
    - No OTP verification required.
    - Checks account status (ACTIVE vs INACTIVE/SUSPENDED).
    - Logs login history.
    - Redirects to appropriate dashboard.
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
                    # Check account active status
                    if user.account_status != 'ACTIVE' or not user.is_active:
                        status_label = user.account_status.lower() if user.account_status else 'inactive'
                        messages.error(request, f"Your account is currently {status_label}. Please contact support.")
                        LoginHistory.objects.create(
                            user=user,
                            username_attempted=identifier,
                            ip_address=ip,
                            user_agent=user_agent,
                            status='FAILED',
                            failure_reason='Account suspended/inactive'
                        )
                        return render(request, 'accounts/login.html', {'form': form})

                    # Direct Login
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


def logout_view(request):
    """Logs out user and clears session."""
    logout(request)
    messages.info(request, "You have been safely signed out.")
    return redirect('accounts:login')


# ============================================================
# 3. FORGOT PASSWORD & PASSWORD RESET (SECURE TOKEN LINK, NO OTP)
# ============================================================

def forgot_password_view(request):
    """
    Handles Forgot Password requests using Django's secure token reset link.
    1. User enters registered email.
    2. Secure, time-limited token is generated.
    3. Password reset link is dispatched via email.
    4. If email service is not configured, displays an informative administrator recovery message.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = CustomUser.objects.filter(email__iexact=email).first()

            if user:
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
                )
                success, msg = send_password_reset_link_email(user, reset_url)

                if success:
                    messages.success(request, "A password reset link has been dispatched to your email address.")
                    return redirect('accounts:password_reset_done')
                else:
                    # Informative message if SMTP offline or not configured
                    messages.error(request, msg)
                    return render(request, 'accounts/forgot_password.html', {'form': form})
            else:
                # Do not leak whether user exists
                messages.info(request, "If an account with that email exists, a password reset link has been sent.")
                return redirect('accounts:password_reset_done')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def password_reset_done_view(request):
    """Displays confirmation that password reset link has been dispatched."""
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    """
    Validates the secure, single-use token and allows user to set a new password.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    validlink = bool(user and default_token_generator.check_token(user, token))

    if not validlink:
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully! You can now sign in with your new password.")
            return redirect('accounts:login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'validlink': True})


# ============================================================
# 4. USER PROFILE & HISTORY
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
