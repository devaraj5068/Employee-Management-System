def notification_context(request):
    """Provides unread notification counts and recent notifications across all views."""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        recent_notifs = request.user.notifications.all()[:6]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifs
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
