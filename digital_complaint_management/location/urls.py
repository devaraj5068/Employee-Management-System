from django.urls import path
from . import views

app_name = 'location'

urlpatterns = [
    path('map/', views.complaint_map_view, name='map_view'),
    path('api/markers/', views.complaint_markers_api, name='markers_api'),
]
