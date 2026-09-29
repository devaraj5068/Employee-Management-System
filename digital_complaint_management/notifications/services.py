import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)

def send_notification(user, title, message, link='', notification_type='INFO', send_email=True):
    """
    Unified notification delivery:
    1. Creates in-app Notification object
    2. Sends email via Django's configured mail backend safely
    """
    if not user:
        return None

    # 1. In-app notification
    notif = Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        link=link,
        notification_type=notification_type
    )

    # 2. Email delivery
    if send_email and user.email:
        try:
            subject = f"[ResolveNow] {title}"
            link_str = f"\nAccess ticket: {link}\n" if link else ""
            email_body = f"""Hello {user.get_full_name() or user.username},

{message}
{link_str}
Thank you,
The ResolveNow Platform Team
"""
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to dispatch email to {user.email}: {e}")

    return notif
