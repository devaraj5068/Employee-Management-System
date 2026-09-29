from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import landing_page, error_403, error_404, error_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('complaints/', include('complaints.urls', namespace='complaints')),
    path('departments/', include('departments.urls', namespace='departments')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('resolutions/', include('resolutions.urls', namespace='resolutions')),
    path('communication/', include('communication.urls', namespace='communication')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('escalation/', include('escalation.urls', namespace='escalation')),
    path('location/', include('location.urls', namespace='location')),
    path('audit/', include('audit.urls', namespace='audit')),
    path('api/', include('api.urls', namespace='api')),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()

handler403 = error_403
handler404 = error_404
handler500 = error_500
