import logging
from .models import ActivityLog, SystemConfiguration

logger = logging.getLogger(__name__)

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_activity(user, action, description, complaint=None, request=None):
    """Utility to seamlessly register an activity audit log."""
    try:
        ip = get_client_ip(request)
        return ActivityLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            action=action,
            description=description,
            ip_address=ip,
            complaint=complaint
        )
    except Exception as e:
        logger.error(f"Failed to write activity log: {e}")
        return None


def get_system_config(key, default=None):
    """Retrieve dynamic system configuration value."""
    try:
        cfg = SystemConfiguration.objects.filter(key=key).first()
        return cfg.value if cfg else default
    except Exception:
        return default
