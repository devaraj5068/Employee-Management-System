import logging
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def is_email_configured():
    """
    Checks if Gmail SMTP configuration variables are properly set.
    Returns (configured: bool, missing_keys: list)
    """
    required = {
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
        'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
    }
    missing = [
        k for k, v in required.items() 
        if not v or str(v).strip() in ['', 'your_email_app_password', 'your_gmail_app_password', '<NEW_GMAIL_APP_PASSWORD>']
    ]
    return len(missing) == 0, missing


def send_otp_email_generic(recipient_email, recipient_name, otp, subject, template_base):
    """
    Core helper to send HTML + Plain text OTP email via Django SMTP email backend.
    template_base is the base template name in templates/emails/.
    Returns (success: bool, user_message: str)
    """
    if not recipient_email:
        return False, "Unable to send verification email. Please try again."

    recipient_email = recipient_email.strip().lower()
    recipient_name = recipient_name or recipient_email.split('@')[0]

    context = {
        'citizen_name': recipient_name,
        'user_name': recipient_name,
        'otp': otp,
        'PLATFORM_NAME': 'ResolveNow',
    }

    try:
        text_content = render_to_string(f'emails/{template_base}.txt', context)
        html_content = render_to_string(f'emails/{template_base}.html', context)
    except Exception as exc:
        logger.exception("Failed to render email template emails/%s: %s", template_base, exc)
        return False, "Unable to send verification email. Please try again."

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info("Successfully dispatched %s email to %s", template_base, recipient_email)
        return True, "Verification code sent successfully to your email."

    except (SMTPAuthenticationError, SMTPConnectError) as exc:
        logger.error("SMTP Authentication/Connection Error for %s: %s", recipient_email, exc)
        return False, "Unable to send verification email. Please try again."
    except (SMTPException, ConnectionError, TimeoutError, OSError) as exc:
        logger.error("SMTP Exception when sending to %s: %s", recipient_email, exc)
        return False, "Unable to send verification email. Please try again."
    except Exception as exc:
        logger.exception("Unexpected error sending email to %s: %s", recipient_email, exc)
        return False, "Unable to send verification email. Please try again."


def send_registration_otp_email(recipient_email, recipient_name, otp):
    """
    Sends Citizen Registration Verification OTP email via Gmail SMTP.
    Subject: ResolveNow – Citizen Registration Verification OTP
    """
    subject = "ResolveNow – Citizen Registration Verification OTP"
    return send_otp_email_generic(recipient_email, recipient_name, otp, subject, 'registration_otp')


# Backwards compatibility alias
send_registration_otp = send_registration_otp_email


def send_login_otp(recipient_email, recipient_name, otp):
    """
    Sends Login Verification OTP email.
    """
    subject = "ResolveNow – Login Verification Code"
    return send_otp_email_generic(recipient_email, recipient_name, otp, subject, 'login_otp')


def send_password_reset_otp(recipient_email, recipient_name, otp):
    """
    Sends Password Reset Verification OTP email.
    """
    subject = "ResolveNow – Password Reset Verification Code"
    return send_otp_email_generic(recipient_email, recipient_name, otp, subject, 'password_reset_otp')
