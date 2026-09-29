from unittest.mock import patch
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from accounts.models import CustomUser, LoginHistory, OTPVerification, TemporaryRegistration


class CitizenRegistrationAndOTPTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an existing citizen
        self.existing_citizen = CustomUser.objects.create_user(
            username='existing_citizen',
            email='existing_citizen@example.com',
            password='Password123!',
            first_name='Existing',
            last_name='Citizen',
            role='CITIZEN',
            is_verified=True,
            account_status='ACTIVE'
        )
        # Create an existing staff member
        self.existing_staff = CustomUser.objects.create_user(
            username='officer_field',
            email='officer_field@resolvenow.org',
            password='Password123!',
            role='STAFF',
            is_verified=True,
            account_status='ACTIVE'
        )
        # Create an existing admin
        self.existing_admin = CustomUser.objects.create_superuser(
            username='admin_boss',
            email='admin_boss@resolvenow.org',
            password='Password123!',
            role='ADMIN',
            is_verified=True,
            account_status='ACTIVE'
        )

    @patch('accounts.views.send_registration_otp_email')
    def test_first_time_registration_creates_temporary_registration_only(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        reg_data = {
            'username': 'fresh_citizen',
            'first_name': 'Fresh',
            'last_name': 'User',
            'email': 'fresh_citizen@example.com',
            'phone_number': '+91 9876543210',
            'address': '123 Resolve Street',
            'password': 'SecureCitizen123!',
            'confirm_password': 'SecureCitizen123!'
        }
        response = self.client.post(reverse('accounts:register'), reg_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:verify_otp'))

        # CRITICAL REQUIREMENT: CustomUser must NOT be created yet
        self.assertFalse(CustomUser.objects.filter(username='fresh_citizen').exists())
        self.assertFalse(CustomUser.objects.filter(email='fresh_citizen@example.com').exists())

        # TemporaryRegistration MUST be created
        temp_reg = TemporaryRegistration.objects.filter(email='fresh_citizen@example.com').first()
        self.assertIsNotNone(temp_reg)
        self.assertEqual(temp_reg.username, 'fresh_citizen')
        self.assertTrue(check_password('SecureCitizen123!', temp_reg.password_hash))

        # OTPVerification must be created and hashed
        otp_rec = OTPVerification.objects.filter(email='fresh_citizen@example.com', purpose='REGISTRATION').first()
        self.assertIsNotNone(otp_rec)
        self.assertFalse(otp_rec.is_verified)
        self.assertIsNone(otp_rec.user)
        # Expiry must be within 5 minutes
        self.assertTrue(otp_rec.expires_at > timezone.now())
        self.assertTrue(otp_rec.expires_at <= timezone.now() + timedelta(minutes=6))

        # Email dispatch was called
        mock_send_email.assert_called_once()

    @patch('accounts.views.send_registration_otp_email')
    def test_registration_duplicate_email_rejected(self, mock_send_email):
        reg_data = {
            'username': 'another_username',
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'existing_citizen@example.com',  # Existing email
            'phone_number': '+91 9876543210',
            'address': 'Street 1',
            'password': 'SecureCitizen123!',
            'confirm_password': 'SecureCitizen123!'
        }
        response = self.client.post(reverse('accounts:register'), reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")
        mock_send_email.assert_not_called()

    @patch('accounts.views.send_registration_otp_email')
    def test_registration_duplicate_username_rejected(self, mock_send_email):
        reg_data = {
            'username': 'existing_citizen',  # Existing username
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'unique_email@example.com',
            'phone_number': '+91 9876543210',
            'address': 'Street 1',
            'password': 'SecureCitizen123!',
            'confirm_password': 'SecureCitizen123!'
        }
        response = self.client.post(reverse('accounts:register'), reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.")
        mock_send_email.assert_not_called()

    @patch('accounts.views.send_registration_otp_email')
    def test_registration_smtp_failure_does_not_create_account(self, mock_send_email):
        mock_send_email.return_value = (False, "Unable to send verification email. Please try again.")

        reg_data = {
            'username': 'failing_smtp_user',
            'first_name': 'Fail',
            'last_name': 'Test',
            'email': 'fail_smtp@example.com',
            'phone_number': '+91 9876543210',
            'address': 'Fail Street',
            'password': 'SecureCitizen123!',
            'confirm_password': 'SecureCitizen123!'
        }
        response = self.client.post(reverse('accounts:register'), reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unable to send verification email. Please try again.")

        # Neither CustomUser nor TemporaryRegistration should persist
        self.assertFalse(CustomUser.objects.filter(username='failing_smtp_user').exists())
        self.assertFalse(TemporaryRegistration.objects.filter(email='fail_smtp@example.com').exists())

    def test_direct_access_verify_otp_without_session_redirects_to_register(self):
        response = self.client.get(reverse('accounts:verify_otp'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:register'))

    @patch('accounts.views.send_registration_otp_email')
    def test_successful_otp_verification_creates_permanent_citizen_account(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        # 1. Register
        reg_data = {
            'username': 'verify_me_citizen',
            'first_name': 'Verify',
            'last_name': 'Me',
            'email': 'verify_me@example.com',
            'phone_number': '+91 9876543210',
            'address': 'Civic Lane',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        self.client.post(reverse('accounts:register'), reg_data)

        # 2. Plant known OTP hash
        otp_rec = OTPVerification.objects.filter(email='verify_me@example.com', purpose='REGISTRATION').first()
        self.assertIsNotNone(otp_rec)
        otp_rec.otp_hash = make_password('654321')
        otp_rec.save()

        # 3. Submit valid OTP
        response = self.client.post(reverse('accounts:verify_otp'), {'otp': '654321'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

        # 4. Check permanent CustomUser created
        user = CustomUser.objects.filter(username='verify_me_citizen').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'verify_me@example.com')
        self.assertEqual(user.role, 'CITIZEN')
        self.assertTrue(user.is_verified)
        self.assertEqual(user.account_status, 'ACTIVE')
        self.assertTrue(user.check_password('SecurePassword123!'))

        # 5. Check TemporaryRegistration deleted
        self.assertFalse(TemporaryRegistration.objects.filter(email='verify_me@example.com').exists())

        # 6. Check OTP marked as verified and used
        otp_rec.refresh_from_db()
        self.assertTrue(otp_rec.is_verified)
        self.assertIsNotNone(otp_rec.used_at)

    @patch('accounts.views.send_registration_otp_email')
    def test_incorrect_otp_rejected_with_attempt_counter(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        reg_data = {
            'username': 'wrong_otp_user',
            'first_name': 'Wrong',
            'last_name': 'OTP',
            'email': 'wrong_otp@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        self.client.post(reverse('accounts:register'), reg_data)

        otp_rec = OTPVerification.objects.filter(email='wrong_otp@example.com', purpose='REGISTRATION').first()
        otp_rec.otp_hash = make_password('112233')
        otp_rec.save()

        # Submit wrong OTP
        response = self.client.post(reverse('accounts:verify_otp'), {'otp': '999999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid OTP. Please try again.")

        # Account must NOT be created
        self.assertFalse(CustomUser.objects.filter(username='wrong_otp_user').exists())

        otp_rec.refresh_from_db()
        self.assertEqual(otp_rec.attempts, 1)

    @patch('accounts.views.send_registration_otp_email')
    def test_five_incorrect_attempts_invalidates_otp(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        reg_data = {
            'username': 'brute_force_user',
            'email': 'bruteforce@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        self.client.post(reverse('accounts:register'), reg_data)

        otp_rec = OTPVerification.objects.filter(email='bruteforce@example.com', purpose='REGISTRATION').first()
        otp_rec.otp_hash = make_password('123456')
        otp_rec.save()

        # Submit 5 incorrect attempts
        for i in range(5):
            self.client.post(reverse('accounts:verify_otp'), {'otp': '000000'})

        otp_rec.refresh_from_db()
        self.assertEqual(otp_rec.attempts, 5)

        # 6th attempt should report max attempts exceeded
        response = self.client.post(reverse('accounts:verify_otp'), {'otp': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Too many incorrect attempts")
        self.assertFalse(CustomUser.objects.filter(username='brute_force_user').exists())

    @patch('accounts.views.send_registration_otp_email')
    def test_expired_otp_is_rejected(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        reg_data = {
            'username': 'expired_user',
            'email': 'expired@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        self.client.post(reverse('accounts:register'), reg_data)

        otp_rec = OTPVerification.objects.filter(email='expired@example.com', purpose='REGISTRATION').first()
        otp_rec.otp_hash = make_password('123456')
        otp_rec.expires_at = timezone.now() - timedelta(minutes=1)  # expired
        otp_rec.save()

        response = self.client.post(reverse('accounts:verify_otp'), {'otp': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OTP has expired. Please request a new OTP.")
        self.assertFalse(CustomUser.objects.filter(username='expired_user').exists())

    @patch('accounts.views.send_registration_otp_email')
    def test_resend_otp_invalidates_old_and_respects_cooldown(self, mock_send_email):
        mock_send_email.return_value = (True, "Verification code sent successfully to your email.")

        reg_data = {
            'username': 'resend_user',
            'email': 'resend@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }
        self.client.post(reverse('accounts:register'), reg_data)

        first_otp = OTPVerification.objects.filter(email='resend@example.com', purpose='REGISTRATION').first()

        # Resend immediately -> Cooldown check should block
        res = self.client.get(reverse('accounts:resend_otp'))
        self.assertEqual(res.status_code, 302)

        # Simulate 65 seconds elapsed
        first_otp.last_sent_at = timezone.now() - timedelta(seconds=65)
        first_otp.save(update_fields=['last_sent_at'])

        # Resend again
        res2 = self.client.get(reverse('accounts:resend_otp'))
        self.assertEqual(res2.status_code, 302)

        # First OTP should be expired/invalidated
        first_otp.refresh_from_db()
        self.assertTrue(first_otp.expires_at <= timezone.now())

        # New active OTP exists
        new_otp = OTPVerification.objects.filter(email='resend@example.com', purpose='REGISTRATION').order_by('-created_at').first()
        self.assertNotEqual(new_otp.id, first_otp.id)
        self.assertTrue(new_otp.expires_at > timezone.now())

    def test_existing_citizen_login_direct_without_otp(self):
        """
        Existing citizens must log in directly to dashboard without any OTP prompt.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'existing_citizen',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        # Redirects to citizen dashboard
        self.assertRedirects(response, reverse('dashboard:user_dashboard'))

        # Check login history record created
        history = LoginHistory.objects.filter(username_attempted='existing_citizen').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.status, 'SUCCESS')

    def test_existing_staff_login_direct_without_otp(self):
        """
        Field officers / staff log in directly to staff dashboard without OTP.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'officer_field',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:staff_dashboard'))

    def test_existing_admin_login_direct_without_otp(self):
        """
        Administrators log in directly to admin dashboard without OTP.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_boss',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:admin_dashboard'))
