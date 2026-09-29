import sys
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from accounts.email_utils import is_email_configured

class Command(BaseCommand):
    help = "Test Gmail SMTP email delivery by sending a test email to a recipient."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Target recipient email address')

    def handle(self, *args, **options):
        recipient = options['email'].strip().lower()
        self.stdout.write("Testing Gmail SMTP...")

        configured, missing = is_email_configured()
        if not configured:
            self.stdout.write(self.style.WARNING(
                f"[WARNING] SMTP email configuration is missing or incomplete: {', '.join(missing)}."
            ))

        self.stdout.write("Sending test email...")

        subject = "ResolveNow – Test Email"
        body = """Hello,

This is a test email sent from the ResolveNow Online Complaint Resolution Platform via Gmail SMTP.

Your Gmail SMTP configuration is operating successfully!

Regards,
ResolveNow Team
Online Complaint Resolution Platform
"""
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False
            )
            self.stdout.write(self.style.SUCCESS("Email sent successfully."))
        except Exception:
            self.stdout.write(self.style.ERROR(
                "Unable to send verification email. Please try again."
            ))
