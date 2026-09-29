import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

def send_otp_email(user, otp):
    """
    Sends a professional HTML & plain-text verification OTP email to user.email.
    Returns (success: bool, message: str).
    """
    if not user or not user.email:
        return False, "User does not have a valid email address configured."

    recipient_name = user.get_full_name() or user.username
    subject = "ResolveNow – Email Verification OTP"

    # Plain text format requested by prompt
    plain_text = f"""Hello {recipient_name},

Your ResolveNow verification OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this OTP, please ignore this email.

Regards,
ResolveNow Team
"""

    # Professional responsive HTML format
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ResolveNow Verification OTP</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 30px 10px;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table width="100%" max-width="540" style="max-width: 540px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden;" border="0" cellspacing="0" cellpadding="0">
          <!-- Header -->
          <tr>
            <td style="background-color: #0f172a; padding: 24px; text-align: center;">
              <h2 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">ResolveNow</h2>
              <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">Online Complaint Resolution Platform</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 32px 28px;">
              <p style="font-size: 15px; color: #1e293b; margin: 0 0 16px 0;">Hello <strong>{recipient_name}</strong>,</p>
              <p style="font-size: 14px; color: #475569; margin: 0 0 20px 0; line-height: 1.5;">
                Thank you for using ResolveNow. Please use the following 6-digit verification code to verify your account:
              </p>
              <div style="background-color: #eff6ff; border: 2px dashed #2563eb; border-radius: 8px; padding: 18px; text-align: center; margin: 24px 0;">
                <span style="font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #1e40af; font-family: 'SFMono-Regular', Consolas, Menlo, monospace;">{otp}</span>
              </div>
              <p style="font-size: 13px; color: #64748b; margin: 0 0 12px 0;">
                &bull; This OTP is valid for <strong>10 minutes</strong>.
              </p>
              <p style="font-size: 13px; color: #64748b; margin: 0 0 20px 0;">
                &bull; Never share this code with anyone. Officials will never ask for your OTP.
              </p>
              <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                If you did not request this OTP, please ignore this email.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
              <p style="font-size: 12px; color: #64748b; margin: 0;">Regards,<br><strong>ResolveNow Team</strong></p>
              <p style="font-size: 11px; color: #94a3b8; margin: 6px 0 0 0;">Civic Administration & Citizen Grievance Portal</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Dispatched verification OTP email to {user.email}")
        return True, "Verification email sent successfully."
    except Exception as e:
        logger.error(f"Failed to dispatch OTP email to {user.email}: {e}")
        # In DEBUG mode, if SMTP fails (e.g. placeholder App Password or network offline),
        # fallback to printing to console so development and testing can proceed smoothly.
        if getattr(settings, 'DEBUG', False):
            try:
                from django.core.mail.backends.console import EmailBackend as ConsoleBackend
                ConsoleBackend().send_messages([msg])
                logger.warning(f"SMTP dispatch failed ({e}). Outputting verification email to console terminal.")
                return True, f"FALLBACK_CONSOLE:{e}"
            except Exception as console_err:
                logger.error(f"Console fallback failed: {console_err}")
        return False, str(e)
