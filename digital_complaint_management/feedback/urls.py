from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('<str:complaint_id>/submit/', views.submit_feedback, name='submit'),
    path('analytics/', views.feedback_analytics, name='analytics'),
]
