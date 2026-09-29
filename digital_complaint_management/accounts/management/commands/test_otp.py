from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CustomUser, OTPVerification
from accounts.email_utils import send_registration_otp, is_email_configured

class Command(BaseCommand):
    help = "Test OTP generation and email dispatch to an existing user or specified email address via Gmail SMTP."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Target recipient email address')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()

        user = CustomUser.objects.filter(email__iexact=email).first()
        recipient_name = user.get_full_name() or user.username if user else email.split('@')[0]

        try:
            plain_otp, otp_instance = OTPVerification.create_otp(
                email=email,
                purpose='REGISTRATION',
                user=user
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating OTP: {e}"))
            return

        success, msg = send_registration_otp(email, recipient_name, plain_otp)

        if success:
            self.stdout.write(self.style.SUCCESS(f"OTP email sent successfully to {email}"))
        else:
            self.stdout.write(self.style.ERROR(f"Verification email could not be sent. Details: {msg}"))
