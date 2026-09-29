from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from departments.models import Department
from complaints.models import Category, SubCategory, Complaint, ComplaintHistory
from complaints.services import register_complaint, generate_complaint_receipt_pdf

class ComplaintTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='adminpassword123',
            role='ADMIN'
        )
        self.officer = CustomUser.objects.create_user(
            username='officer_test',
            email='officer@test.com',
            password='officerpassword123',
            role='STAFF',
            is_staff=True
        )
        self.citizen = CustomUser.objects.create_user(
            username='citizen_test',
            email='citizen@test.com',
            password='citizenpassword123',
            role='CITIZEN',
            is_verified=True
        )
        self.other_citizen = CustomUser.objects.create_user(
            username='other_citizen',
            email='other@test.com',
            password='citizenpassword123',
            role='CITIZEN',
            is_verified=True
        )

        self.dept = Department.objects.create(
            name='Test Roads',
            code='TRD',
            description='Test department'
        )

        self.cat = Category.objects.create(
            name='Test Potholes',
            department=self.dept,
            default_priority='HIGH'
        )

        self.subcat = SubCategory.objects.create(
            category=self.cat,
            name='Crater'
        )

    def test_complaint_id_format(self):
        cid = Complaint.generate_complaint_id()
        current_year = timezone.now().year
        self.assertTrue(cid.startswith(f"RN-{current_year}-"))
        self.assertEqual(len(cid), 14)  # RN-2026-000001

    def test_complaint_creation_service(self):
        data = {
            'title': 'Dangerous Road Crater',
            'description': 'Road has huge pothole causing hazard.',
            'category': self.cat,
            'subcategory': self.subcat,
            'priority': 'HIGH',
            'location_address': 'Main Highway 10',
            'latitude': 12.9716,
            'longitude': 77.5946
        }
        complaint = register_complaint(self.citizen, data, files=[])
        self.assertIsNotNone(complaint.id)
        self.assertTrue(complaint.complaint_id.startswith('RN-'))
        self.assertEqual(complaint.department, self.dept)
        self.assertEqual(complaint.priority, 'HIGH')
        self.assertEqual(complaint.status, 'SUBMITTED')

        # Check initial history log
        h = ComplaintHistory.objects.filter(complaint=complaint).first()
        self.assertIsNotNone(h)
        self.assertEqual(h.new_status, 'SUBMITTED')

    def test_status_update_and_history_logging(self):
        complaint = Complaint.objects.create(
            complaint_id=Complaint.generate_complaint_id(),
            user=self.citizen,
            title='Water Leak',
            description='Pipe is leaking.',
            category=self.cat,
            department=self.dept,
            status='SUBMITTED'
        )

        self.client.login(username='officer_test', password='officerpassword123')
        response = self.client.post(reverse('complaints:status_update', args=[complaint.complaint_id]), {
            'status': 'IN_PROGRESS',
            'remarks': 'Field crew has reached the site.'
        })
        self.assertEqual(response.status_code, 302)

        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'IN_PROGRESS')

        # Verify history log created
        history_entry = ComplaintHistory.objects.filter(complaint=complaint, new_status='IN_PROGRESS').first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.remarks, 'Field crew has reached the site.')
        self.assertEqual(history_entry.changed_by, self.officer)

    def test_permissions_citizen_isolation(self):
        complaint = Complaint.objects.create(
            complaint_id=Complaint.generate_complaint_id(),
            user=self.citizen,
            title='Private Issue',
            description='Confidential report.',
            category=self.cat,
            department=self.dept
        )

        # Other citizen tries to view
        self.client.login(username='other_citizen', password='citizenpassword123')
        response = self.client.get(reverse('complaints:detail', args=[complaint.complaint_id]))
        self.assertEqual(response.status_code, 302)  # Redirected due to access restriction

    def test_permissions_user_cannot_access_admin_pages(self):
        self.client.login(username='citizen_test', password='citizenpassword123')
        response = self.client.get(reverse('departments:list'))
        self.assertEqual(response.status_code, 302)  # Redirected away from admin view

    def test_pdf_receipt_generation(self):
        complaint = Complaint.objects.create(
            complaint_id='RN-2026-000099',
            user=self.citizen,
            title='Broken Light',
            description='Street lamp broken on 3rd cross.',
            category=self.cat,
            department=self.dept,
            due_date=timezone.now()
        )
        pdf_buf = generate_complaint_receipt_pdf(complaint)
        self.assertGreater(pdf_buf.getbuffer().nbytes, 1000)
        self.assertTrue(pdf_buf.getvalue().startswith(b'%PDF'))
