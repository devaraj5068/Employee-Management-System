from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from complaints.models import Complaint, ComplaintHistory
from .models import EscalationLog, EscalationRule
from .services import check_and_escalate_overdue_complaints
from accounts.decorators import admin_required
from notifications.services import send_notification
from audit.services import log_activity

@admin_required
def escalation_dashboard(request):
    """Admin dashboard for monitoring all escalated and overdue tickets."""
    escalated_complaints = Complaint.objects.filter(is_escalated=True).exclude(status__in=['RESOLVED', 'CLOSED']).select_related('department', 'assigned_staff', 'user')
    logs = EscalationLog.objects.select_related('complaint', 'triggered_by').all()[:50]
    rules = EscalationRule.objects.all()

    return render(request, 'escalation/dashboard.html', {
        'escalated_complaints': escalated_complaints,
        'logs': logs,
        'rules': rules
    })


@admin_required
def run_escalation_scan(request):
    """Manual trigger from admin dashboard to scan for SLA violations."""
    count = check_and_escalate_overdue_complaints()
    messages.success(request, f"SLA scan completed. {count} ticket(s) escalated.")
    return redirect('escalation:dashboard')


@login_required
def manual_escalate(request, complaint_id):
    """Allows admin, department head, or citizen to manually escalate a stagnant complaint."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    user = request.user

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "A reason for escalation is required.")
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)

        complaint.is_escalated = True
        complaint.escalation_level = min(4, complaint.escalation_level + 1)
        complaint.escalation_reason = reason
        complaint.save()

        EscalationLog.objects.create(
            complaint=complaint,
            level=complaint.escalation_level,
            reason=f"Manual escalation by {user.get_full_name() or user.username}: {reason}",
            triggered_by=user,
            is_automated=False
        )

        ComplaintHistory.objects.create(
            complaint=complaint,
            previous_status=complaint.status,
            new_status=complaint.status,
            changed_by=user,
            remarks=f"Manually escalated to Level {complaint.escalation_level}: {reason}"
        )

        log_activity(
            user=user,
            action='ESCALATE',
            description=f"Manually escalated {complaint.complaint_id} to Level {complaint.escalation_level}: {reason}",
            complaint=complaint,
            request=request
        )

        messages.warning(request, f"Complaint {complaint.complaint_id} has been escalated to Level {complaint.escalation_level}.")
    return redirect('complaints:detail', complaint_id=complaint.complaint_id)
