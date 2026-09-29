from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
