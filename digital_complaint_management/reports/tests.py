from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from departments.models import Department
from complaints.models import Category, Complaint

class ReportExportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_superuser(
            username='admin_report',
            email='admin@report.com',
            password='adminpassword123',
            role='ADMIN'
        )
        self.client.login(username='admin_report', password='adminpassword123')

        dept = Department.objects.create(name='Sanitation', code='SAN')
        cat = Category.objects.create(name='Waste', department=dept)
        Complaint.objects.create(
            complaint_id='RN-2026-999991',
            user=self.admin,
            title='Sample Garbage Issue',
            description='Dump on sidewalk.',
            category=cat,
            department=dept
        )

    def test_export_pdf_report(self):
        response = self.client.get(reverse('reports:export_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_export_excel_report(self):
        response = self.client.get(reverse('reports:export_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertGreater(len(response.content), 2000)

    def test_export_csv_report(self):
        response = self.client.get(reverse('reports:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(b'Complaint ID,Title', response.content)
