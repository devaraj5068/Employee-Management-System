from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='list'),
    path('create/', views.staff_create, name='create'),
    path('<int:pk>/edit/', views.staff_update, name='update'),
    path('workload/', views.staff_workload_dashboard, name='workload'),
]
