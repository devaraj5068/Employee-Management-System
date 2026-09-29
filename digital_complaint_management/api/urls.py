from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register('complaints', views.ComplaintViewSet, basename='complaint')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('staff', views.StaffViewSet, basename='staff')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('feedback', views.FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('auth/login/', views.AuthLoginAPI.as_view(), name='api_login'),
    path('auth/user/', views.CurrentUserAPI.as_view(), name='api_user'),
    path('reports/summary/', views.ReportSummaryAPI.as_view(), name='api_report_summary'),
    path('', include(router.urls)),
]
