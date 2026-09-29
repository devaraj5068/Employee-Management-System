from django.urls import path
from . import views

app_name = 'escalation'

urlpatterns = [
    path('', views.escalation_dashboard, name='dashboard'),
    path('scan/', views.run_escalation_scan, name='scan'),
    path('<str:complaint_id>/manual/', views.manual_escalate, name='manual_escalate'),
]
