from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Resolution
from .forms import ResolutionSubmissionForm, ResolutionVerificationForm, ComplaintReopenForm
from complaints.models import Complaint, ComplaintHistory
from notifications.services import send_notification
from audit.services import log_activity
from django.urls import reverse

@login_required
def submit_resolution(request, complaint_id):
    """Staff officer submits resolution summary, proof photos, and documents."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    user = request.user

    # Only assigned staff or admin can submit resolution
    if not (complaint.assigned_staff == user or user.role == 'ADMIN' or user.is_superuser):
        messages.error(request, "Only the assigned field officer or an administrator can submit a resolution.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if hasattr(complaint, 'resolution'):
        messages.info(request, "A resolution has already been submitted for this complaint.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ResolutionSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            resolution = form.save(commit=False)
            resolution.complaint = complaint
            resolution.resolved_by = user
            resolution.verification_status = 'APPROVED'  # standard auto-approval, admin can also verify
            resolution.save()

            # Update complaint status to RESOLVED
            prev_status = complaint.status
            complaint.status = 'RESOLVED'
            complaint.closed_at = timezone.now()
            complaint.save()

            ComplaintHistory.objects.create(
                complaint=complaint,
                previous_status=prev_status,
                new_status='RESOLVED',
                changed_by=user,
                remarks=f"Resolution submitted by {user.get_full_name() or user.username}: {resolution.description[:100]}"
            )

            log_activity(
                user=user,
                action='RESOLVE',
                description=f"Submitted resolution for {complaint.complaint_id}",
                complaint=complaint,
                request=request
            )

            # Notify Citizen
            detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
            send_notification(
                user=complaint.user,
                title="Your Complaint has been Resolved!",
                message=f"Complaint [{complaint.complaint_id}] has been resolved. Please review the resolution and submit your feedback.",
                link=detail_url
            )

            messages.success(request, "Resolution successfully submitted! The citizen has been notified.")
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)
    else:
        form = ResolutionSubmissionForm()

    return render(request, 'resolutions/submit_resolution.html', {
        'form': form,
        'complaint': complaint
    })


@login_required
def verify_resolution(request, complaint_id):
    """Admin quality assurance check: approve or reject resolution."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser):
        messages.error(request, "Access restricted to administrators.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    resolution = getattr(complaint, 'resolution', None)
    if not resolution:
        messages.error(request, "No resolution exists to verify.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ResolutionVerificationForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            comments = form.cleaned_data['comments']

            resolution.verified_by = request.user
            resolution.verified_at = timezone.now()

            if decision == 'APPROVE':
                resolution.verification_status = 'APPROVED'
                complaint.status = 'CLOSED'
                complaint.save()
                
                ComplaintHistory.objects.create(
                    complaint=complaint,
                    previous_status='RESOLVED',
                    new_status='CLOSED',
                    changed_by=request.user,
                    remarks=f"Resolution quality approved by Admin. Complaint closed. Notes: {comments}"
                )
                messages.success(request, "Resolution approved and complaint marked Closed.")
            else:
                resolution.verification_status = 'REJECTED'
                resolution.rejection_reason = comments
                complaint.status = 'IN_PROGRESS'
                complaint.save()

                ComplaintHistory.objects.create(
                    complaint=complaint,
                    previous_status='RESOLVED',
                    new_status='IN_PROGRESS',
                    changed_by=request.user,
                    remarks=f"Resolution REJECTED by Admin. Returned to officer for rework. Reason: {comments}"
                )
                if complaint.assigned_staff:
                    detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
                    send_notification(
                        user=complaint.assigned_staff,
                        title="Resolution Rejected - Action Required",
                        message=f"Admin returned [{complaint.complaint_id}] for rework. Reason: {comments}",
                        link=detail_url
                    )
                messages.warning(request, "Resolution rejected. Complaint has been returned to In Progress.")

            resolution.save()
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)
    else:
        form = ResolutionVerificationForm()

    return render(request, 'resolutions/verify_resolution.html', {
        'form': form,
        'complaint': complaint,
        'resolution': resolution
    })


@login_required
def reopen_complaint(request, complaint_id):
    """Citizen reopens a resolved complaint if dissatisfied."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.user != complaint.user and not (request.user.role == 'ADMIN' or request.user.is_superuser):
        messages.error(request, "Only the complaint author or an admin may reopen this ticket.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if complaint.status not in ['RESOLVED', 'CLOSED']:
        messages.error(request, "Only resolved or closed complaints can be reopened.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ComplaintReopenForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            prev_status = complaint.status
            complaint.status = 'REOPENED'
            complaint.is_escalated = True
            complaint.save()

            ComplaintHistory.objects.create(
                complaint=complaint,
                previous_status=prev_status,
                new_status='REOPENED',
                changed_by=request.user,
                remarks=f"Reopened by user: {reason}"
            )

            log_activity(
                user=request.user,
                action='REOPEN',
                description=f"Reopened complaint {complaint.complaint_id}: {reason}",
                complaint=complaint,
                request=request
            )

            # Notify assigned officer and admin
            detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
            if complaint.assigned_staff:
                send_notification(
                    user=complaint.assigned_staff,
                    title="Complaint Reopened by Citizen",
                    message=f"Complaint [{complaint.complaint_id}] was reopened. Reason: {reason}",
                    link=detail_url
                )

            messages.warning(request, f"Complaint {complaint.complaint_id} has been reopened and escalated for re-investigation.")
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)
    else:
        form = ComplaintReopenForm()

    return render(request, 'resolutions/reopen_complaint.html', {
        'form': form,
        'complaint': complaint
    })
