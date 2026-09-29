from django.conf import settings
from .models import SystemConfiguration

def system_configuration_context(request):
    """Context processor providing platform settings and map tile configuration across all templates."""
    try:
        configs = {c.key: c.value for c in SystemConfiguration.objects.all()}
    except Exception:
        configs = {}

    return {
        'PLATFORM_NAME': configs.get('PLATFORM_NAME', 'ResolveNow'),
        'PLATFORM_TAGLINE': configs.get('PLATFORM_TAGLINE', 'Online Complaint Resolution Platform'),
        'SUPPORT_EMAIL': configs.get('SUPPORT_EMAIL', 'support@resolvenow.org'),
        'SUPPORT_PHONE': configs.get('SUPPORT_PHONE', '1800-CIVIC-HELP'),
        'ALLOW_REOPEN_DAYS': configs.get('ALLOW_REOPEN_DAYS', '7'),
        'MAP_TILE_URL': getattr(settings, 'MAP_TILE_URL', 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'),
        'MAP_TILE_ATTRIBUTION': getattr(settings, 'MAP_TILE_ATTRIBUTION', '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
    }
