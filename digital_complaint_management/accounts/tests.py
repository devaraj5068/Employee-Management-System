from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from accounts.models import CustomUser, LoginHistory


class RemoveEmailVerificationAndOTPTests(TestCase):
    """
    Tests ensuring complete removal of email verification and OTP
    across registration, login, and forgot password flows.
    """

    def setUp(self):
        self.client = Client()
        # Existing Citizen
        self.citizen = CustomUser.objects.create_user(
            username='citizen_john',
            email='citizen_john@example.com',
            password='CitizenPassword123!',
            first_name='John',
            last_name='Citizen',
            role='CITIZEN',
            is_verified=True,
            account_status='ACTIVE'
        )
        # Existing Staff
        self.officer = CustomUser.objects.create_user(
            username='officer_water',
            email='officer_water@resolvenow.org',
            password='StaffPassword123!',
            first_name='Water',
            last_name='Officer',
            role='STAFF',
            is_verified=True,
            account_status='ACTIVE'
        )
        # Existing Admin
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@resolvenow.org',
            password='AdminPassword123!',
            first_name='System',
            last_name='Admin',
            role='ADMIN',
            is_verified=True,
            account_status='ACTIVE'
        )

    # ------------------------------------------------------------
    # Test 1: New Citizen Registration (Direct, No OTP, Redirect to Login)
    # ------------------------------------------------------------
    def test_1_new_citizen_registration_direct_without_otp(self):
        reg_data = {
            'username': 'new_citizen_user',
            'first_name': 'New',
            'last_name': 'Citizen',
            'email': 'newcitizen@example.com',
            'phone_number': '+91 9876543210',
            'address': '123 MG Road, Bengaluru',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        response = self.client.post(reverse('accounts:register'), reg_data)

        # Directly redirects to Login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

        # Permanent CustomUser is created directly with ACTIVE status and hashed password
        user = CustomUser.objects.filter(username='new_citizen_user').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newcitizen@example.com')
        self.assertEqual(user.role, 'CITIZEN')
        self.assertTrue(user.is_active)
        self.assertEqual(user.account_status, 'ACTIVE')
        self.assertTrue(user.is_verified)
        self.assertTrue(user.check_password('StrongPassword123!'))

    # ------------------------------------------------------------
    # Test 2: Duplicate Registration Check
    # ------------------------------------------------------------
    def test_2_duplicate_registration_rejected(self):
        # Duplicate Username
        dup_user_data = {
            'username': 'citizen_john',  # Existing
            'first_name': 'Different',
            'last_name': 'Name',
            'email': 'different_email@example.com',
            'phone_number': '+91 9876543210',
            'address': '456 Residency Road',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        res1 = self.client.post(reverse('accounts:register'), dup_user_data)
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, "A user with that username already exists.")

        # Duplicate Email
        dup_email_data = {
            'username': 'unique_user_2',
            'first_name': 'Different',
            'last_name': 'Name',
            'email': 'citizen_john@example.com',  # Existing email
            'phone_number': '+91 9876543210',
            'address': '456 Residency Road',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        res2 = self.client.post(reverse('accounts:register'), dup_email_data)
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "An account with this email already exists.")

        # Ensure no second user was created
        self.assertEqual(CustomUser.objects.filter(email='citizen_john@example.com').count(), 1)

    # ------------------------------------------------------------
    # Test 3: Citizen Login (Direct, No OTP)
    # ------------------------------------------------------------
    def test_3_citizen_login_without_otp(self):
        login_data = {
            'username': 'citizen_john',
            'password': 'CitizenPassword123!'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:user_dashboard'))

        # Check authenticated session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.citizen.id)

        # LoginHistory record is SUCCESS
        history = LoginHistory.objects.filter(user=self.citizen, status='SUCCESS').first()
        self.assertIsNotNone(history)

    # ------------------------------------------------------------
    # Test 4: Invalid Login
    # ------------------------------------------------------------
    def test_4_invalid_login_rejected(self):
        login_data = {
            'username': 'citizen_john',
            'password': 'WrongPassword999!'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password.")
        self.assertNotIn('_auth_user_id', self.client.session)

    # ------------------------------------------------------------
    # Test 5: Forgot Password Dispatches Secure Token Link (No OTP)
    # ------------------------------------------------------------
    @patch('accounts.views.send_password_reset_link_email')
    def test_5_forgot_password_sends_token_link_without_otp(self, mock_send_email):
        mock_send_email.return_value = (True, "A password reset link has been dispatched to your email address.")

        response = self.client.post(reverse('accounts:forgot_password'), {
            'email': 'citizen_john@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:password_reset_done'))

        # Email dispatch was called with user and URL containing token
        mock_send_email.assert_called_once()
        user_arg, reset_url_arg = mock_send_email.call_args[0]
        self.assertEqual(user_arg, self.citizen)
        self.assertIn('/accounts/password-reset/confirm/', reset_url_arg)
        self.assertNotIn('otp', reset_url_arg.lower())

    # ------------------------------------------------------------
    # Test 6: Password Reset with Valid Token
    # ------------------------------------------------------------
    def test_6_password_reset_confirm_with_valid_token(self):
        token = default_token_generator.make_token(self.citizen)
        uidb64 = urlsafe_base64_encode(force_bytes(self.citizen.pk))

        confirm_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        get_res = self.client.get(confirm_url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Set New Password")

        post_res = self.client.post(confirm_url, {
            'new_password': 'BrandNewPassword456!',
            'confirm_password': 'BrandNewPassword456!'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertRedirects(post_res, reverse('accounts:login'))

        # Verify new password is set
        self.citizen.refresh_from_db()
        self.assertTrue(self.citizen.check_password('BrandNewPassword456!'))

        # Verify login works with new password
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'citizen_john',
            'password': 'BrandNewPassword456!'
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertRedirects(login_res, reverse('dashboard:user_dashboard'))

    # ------------------------------------------------------------
    # Test 7: Expired or Used Reset Link Rejected
    # ------------------------------------------------------------
    def test_7_expired_or_used_token_rejected(self):
        token = default_token_generator.make_token(self.citizen)
        uidb64 = urlsafe_base64_encode(force_bytes(self.citizen.pk))
        confirm_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        # Use the token once
        self.client.post(confirm_url, {
            'new_password': 'ResetPassOnce123!',
            'confirm_password': 'ResetPassOnce123!'
        })

        # Try using the same token a second time
        res_used = self.client.get(confirm_url)
        self.assertEqual(res_used.status_code, 200)
        self.assertContains(res_used, "Invalid or Expired Link")

        # Invalid token string
        invalid_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': 'fake-invalid-token'})
        res_invalid = self.client.get(invalid_url)
        self.assertEqual(res_invalid.status_code, 200)
        self.assertContains(res_invalid, "Invalid or Expired Link")

    # ------------------------------------------------------------
    # Test 8: Role-Based Access and Inactive Account Control
    # ------------------------------------------------------------
    def test_8_role_based_access_and_inactive_controls(self):
        # Admin login redirects to admin dashboard
        self.client.post(reverse('accounts:login'), {
            'username': 'admin',
            'password': 'AdminPassword123!'
        })
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin.id)
        self.client.logout()

        # Staff login redirects to staff dashboard
        self.client.post(reverse('accounts:login'), {
            'username': 'officer_water',
            'password': 'StaffPassword123!'
        })
        self.assertEqual(int(self.client.session['_auth_user_id']), self.officer.id)
        self.client.logout()

        # Inactive user is rejected
        self.citizen.account_status = 'INACTIVE'
        self.citizen.save()
        res_inactive = self.client.post(reverse('accounts:login'), {
            'username': 'citizen_john',
            'password': 'CitizenPassword123!'
        })
        self.assertEqual(res_inactive.status_code, 200)
        self.assertContains(res_inactive, "Your account is currently inactive")
        self.assertNotIn('_auth_user_id', self.client.session)

    # ------------------------------------------------------------
    # Test 9: Existing Features Preservation (Complaints Access)
    # ------------------------------------------------------------
    def test_9_existing_features_accessible(self):
        self.client.force_login(self.citizen)
        # Dashboard index
        dash_res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(dash_res.status_code, 302)

        # Complaints list
        list_res = self.client.get(reverse('complaints:list'))
        self.assertEqual(list_res.status_code, 200)

        # Register complaint page
        create_res = self.client.get(reverse('complaints:create'))
        self.assertEqual(create_res.status_code, 200)

    # ------------------------------------------------------------
    # Test 10: No Remaining OTP Flow or Routes
    # ------------------------------------------------------------
    def test_10_no_remaining_otp_routes(self):
        # Obsolete OTP routes return 404
        self.assertEqual(self.client.get('/accounts/verify-otp/').status_code, 404)
        self.assertEqual(self.client.get('/accounts/resend-otp/').status_code, 404)
        self.assertEqual(self.client.get('/accounts/login-otp/').status_code, 404)
        self.assertEqual(self.client.get('/accounts/password-reset-otp/').status_code, 404)
