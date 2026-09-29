from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('register/', views.complaint_create, name='create'),
    path('track/', views.complaint_track_public, name='track'),
    path('ajax/subcategories/', views.subcategories_ajax, name='ajax_subcategories'),
    
    # Specific complaint actions
    path('<str:complaint_id>/', views.complaint_detail, name='detail'),
    path('<str:complaint_id>/receipt/', views.complaint_receipt_view, name='receipt'),
    path('<str:complaint_id>/receipt/pdf/', views.complaint_receipt_pdf_download, name='receipt_pdf'),
    path('<str:complaint_id>/status/', views.complaint_status_update, name='status_update'),
    path('<str:complaint_id>/assign/', views.complaint_assign, name='assign'),
    path('<str:complaint_id>/priority/', views.complaint_priority_update, name='priority_update'),

    # Category admin management
    path('admin/categories/', views.category_list, name='category_list'),
    path('admin/categories/create/', views.category_create, name='category_create'),
    path('admin/categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('admin/categories/<int:category_id>/subcategories/create/', views.subcategory_create, name='subcategory_create'),
]
