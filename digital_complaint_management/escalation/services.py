import logging
from django.utils import timezone
from datetime import timedelta
from complaints.models import Complaint, ComplaintHistory
from accounts.models import CustomUser
from .models import EscalationLog
from notifications.services import send_notification
from audit.services import log_activity
from django.urls import reverse

logger = logging.getLogger(__name__)

def check_and_escalate_overdue_complaints():
    """
    Automated SLA scanner:
    Finds all active non-resolved complaints that passed due_date.
    Advances escalation level, flags complaint as escalated, and dispatches alerts.
    """
    now = timezone.now()
    overdue_complaints = Complaint.objects.filter(
        due_date__lt=now
    ).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED'])

    escalated_count = 0

    for comp in overdue_complaints:
        new_level = min(4, comp.escalation_level + 1)
        reason = f"SLA Breach: Exceeded resolution deadline of {comp.due_date:%Y-%m-%d %H:%M}."

        # If not already marked escalated or level increased
        if not comp.is_escalated or comp.escalation_level < new_level:
            comp.is_escalated = True
            comp.escalation_level = new_level
            comp.save(update_fields=['is_escalated', 'escalation_level', 'updated_at'])

            EscalationLog.objects.create(
                complaint=comp,
                level=new_level,
                reason=reason,
                triggered_by=None,
                is_automated=True
            )

            ComplaintHistory.objects.create(
                complaint=comp,
                previous_status=comp.status,
                new_status=comp.status,
                changed_by=None,
                remarks=f"AUTOMATED SLA BREACH: Escalated to Level {new_level}. Overdue since {comp.due_date:%Y-%m-%d}."
            )

            # Notify Admin and Staff
            detail_url = reverse('complaints:detail', kwargs={'complaint_id': comp.complaint_id})
            admin_users = CustomUser.objects.filter(role='ADMIN', is_active=True)
            for adm in admin_users:
                send_notification(
                    user=adm,
                    title=f"URGENT: Complaint [{comp.complaint_id}] Escalated to Level {new_level}",
                    message=f"Ticket '{comp.title}' has breached SLA. Assigned staff: {comp.assigned_staff.get_full_name() if comp.assigned_staff else 'Unassigned'}.",
                    link=detail_url,
                    notification_type='URGENT'
                )

            if comp.assigned_staff:
                send_notification(
                    user=comp.assigned_staff,
                    title=f"CRITICAL OVERDUE ALERT: [{comp.complaint_id}] Escalated",
                    message=f"Your ticket '{comp.title}' is overdue and has been escalated to Level {new_level}.",
                    link=detail_url,
                    notification_type='URGENT'
                )

            escalated_count += 1

    return escalated_count
