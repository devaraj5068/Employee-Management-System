from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_analytics_view, name='analytics'),
    path('export/pdf/', views.export_pdf_report, name='export_pdf'),
    path('export/excel/', views.export_excel_report, name='export_excel'),
    path('export/csv/', views.export_csv_report, name='export_csv'),
]
