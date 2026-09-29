from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('<str:complaint_id>/send/', views.post_message, name='post_message'),
    path('<str:complaint_id>/message/', views.post_message, name='send_message'),
]
