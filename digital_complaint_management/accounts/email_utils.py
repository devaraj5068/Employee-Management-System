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


def send_password_reset_link_email(user, reset_url):
    """
    Sends secure password reset link email via Django SMTP email backend.
    Returns (success: bool, user_message: str)
    """
    if not user or not user.email:
        return False, "User does not have a registered email address."

    configured, missing = is_email_configured()
    if not configured:
        logger.warning("SMTP email delivery is not configured. Missing keys: %s", missing)
        return False, "Email delivery service is currently not configured. Please contact the system administrator to reset your password."

    recipient_email = user.email.strip().lower()
    recipient_name = user.get_full_name() or user.username
    subject = "ResolveNow – Password Reset Request"

    context = {
        'user_name': recipient_name,
        'reset_url': reset_url,
        'PLATFORM_NAME': 'ResolveNow',
    }

    try:
        text_content = render_to_string('emails/password_reset_email.txt', context)
        html_content = render_to_string('emails/password_reset_email.html', context)
    except Exception as exc:
        logger.exception("Failed to render password reset email template: %s", exc)
        return False, "Unable to generate password reset email. Please try again."

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
        logger.info("Successfully dispatched password reset link to %s", recipient_email)
        return True, "A password reset link has been dispatched to your email address."

    except (SMTPAuthenticationError, SMTPConnectError) as exc:
        logger.error("SMTP Authentication/Connection Error for %s: %s", recipient_email, exc)
        return False, "Email delivery server authentication failed. Please contact your system administrator."
    except (SMTPException, ConnectionError, TimeoutError, OSError) as exc:
        logger.error("SMTP Exception when sending to %s: %s", recipient_email, exc)
        return False, "Unable to dispatch password reset email at this time. Please contact support or try again later."
    except Exception as exc:
        logger.exception("Unexpected error sending email to %s: %s", recipient_email, exc)
        return False, "Unable to dispatch password reset email. Please contact support."
