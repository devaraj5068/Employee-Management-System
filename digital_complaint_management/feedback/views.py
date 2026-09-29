from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import ComplaintFeedback
from .forms import ComplaintFeedbackForm
from complaints.models import Complaint
from accounts.decorators import admin_required
from audit.services import log_activity

@login_required
def submit_feedback(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)

    # Only original citizen can submit feedback
    if request.user != complaint.user:
        messages.error(request, "Only the citizen who filed this complaint can submit feedback.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    # Must be resolved or closed
    if complaint.status not in ['RESOLVED', 'CLOSED']:
        messages.error(request, "Feedback can only be submitted after the complaint is resolved.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if hasattr(complaint, 'feedback'):
        messages.info(request, "Feedback has already been submitted for this complaint.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ComplaintFeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.complaint = complaint
            fb.user = request.user
            fb.save()

            log_activity(
                user=request.user,
                action='UPDATE',
                description=f"Submitted feedback for {complaint.complaint_id}: {fb.rating}/5 stars",
                complaint=complaint,
                request=request
            )

            messages.success(request, "Thank you for your valuable feedback! It helps improve our municipal services.")
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)
    else:
        form = ComplaintFeedbackForm()

    return render(request, 'feedback/submit.html', {'form': form, 'complaint': complaint})


@admin_required
def feedback_analytics(request):
    feedbacks = ComplaintFeedback.objects.select_related('complaint', 'user', 'complaint__department', 'complaint__assigned_staff').all()
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0
    total_feedbacks = feedbacks.count()

    rating_breakdown = feedbacks.values('rating').annotate(total=Count('id')).order_by('-rating')
    
    return render(request, 'feedback/analytics.html', {
        'feedbacks': feedbacks[:50],
        'avg_rating': round(avg_rating, 2),
        'total_feedbacks': total_feedbacks,
        'rating_breakdown': rating_breakdown,
    })
