from django.urls import path
from . import views

app_name = 'resolutions'

urlpatterns = [
    path('<str:complaint_id>/submit/', views.submit_resolution, name='submit'),
    path('<str:complaint_id>/create/', views.submit_resolution, name='create'),
    path('<str:complaint_id>/verify/', views.verify_resolution, name='verify'),
    path('<str:complaint_id>/reopen/', views.reopen_complaint, name='reopen'),
]
