from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from departments.models import Department
from complaints.models import Category, Complaint, ComplaintHistory
from resolutions.models import Resolution

class ResolutionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_superuser(
            username='admin_res',
            email='admin@res.com',
            password='password123',
            role='ADMIN'
        )
        self.officer = CustomUser.objects.create_user(
            username='officer_res',
            email='officer@res.com',
            password='password123',
            role='STAFF',
            is_staff=True
        )
        self.citizen = CustomUser.objects.create_user(
            username='citizen_res',
            email='citizen@res.com',
            password='password123',
            role='CITIZEN',
            is_verified=True
        )

        dept = Department.objects.create(name='Water', code='WTR')
        cat = Category.objects.create(name='Pipes', department=dept)
        self.complaint = Complaint.objects.create(
            complaint_id='RN-2026-888888',
            user=self.citizen,
            title='Pipeline Leak',
            description='Main line burst.',
            category=cat,
            department=dept,
            assigned_staff=self.officer,
            status='IN_PROGRESS'
        )

    def test_officer_resolution_submission(self):
        self.client.login(username='officer_res', password='password123')
        response = self.client.post(reverse('resolutions:submit', args=[self.complaint.complaint_id]), {
            'description': 'Replaced broken valve and welded section.',
            'remarks': 'Tested pressure up to 4 bar.'
        })
        self.assertEqual(response.status_code, 302)

        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'RESOLVED')
        self.assertTrue(hasattr(self.complaint, 'resolution'))
        self.assertEqual(self.complaint.resolution.resolved_by, self.officer)

    def test_citizen_reopen_complaint(self):
        self.complaint.status = 'RESOLVED'
        self.complaint.save()

        self.client.login(username='citizen_res', password='password123')
        response = self.client.post(reverse('resolutions:reopen', args=[self.complaint.complaint_id]), {
            'reason': 'Water leakage has started again from the adjacent weld joint.'
        })
        self.assertEqual(response.status_code, 302)

        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'REOPENED')
        self.assertTrue(self.complaint.is_escalated)
