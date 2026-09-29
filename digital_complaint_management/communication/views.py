from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ComplaintMessage
from .forms import ComplaintMessageForm
from complaints.models import Complaint
from notifications.services import send_notification
from django.urls import reverse

@login_required
def post_message(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    user = request.user

    # Security check: User must be either author, assigned staff, or admin
    if user.role == 'CITIZEN' and complaint.user != user:
        messages.error(request, "Permission denied.")
        return redirect('complaints:list')

    if request.method == 'POST':
        form = ComplaintMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.complaint = complaint
            msg.sender = user

            # Only staff or admin can mark internal notes
            if user.role == 'CITIZEN':
                msg.is_internal = False

            msg.save()

            # Notifications
            if not msg.is_internal:
                detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
                if user.role == 'CITIZEN':
                    # Notify assigned officer
                    if complaint.assigned_staff:
                        send_notification(
                            user=complaint.assigned_staff,
                            title=f"New Message on [{complaint.complaint_id}]",
                            message=f"{user.get_full_name() or user.username}: {msg.message[:80]}",
                            link=detail_url
                        )
                else:
                    # Notify citizen
                    send_notification(
                        user=complaint.user,
                        title=f"Update on Complaint [{complaint.complaint_id}]",
                        message=f"Officer {user.get_full_name() or user.username} replied: {msg.message[:80]}",
                        link=detail_url
                    )

            messages.success(request, "Message posted to discussion thread.")
    return redirect('complaints:detail', complaint_id=complaint.complaint_id)
