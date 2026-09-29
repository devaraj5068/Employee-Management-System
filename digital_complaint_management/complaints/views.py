from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Complaint, ComplaintAttachment, ComplaintHistory, Category, SubCategory
from departments.models import Department
from .forms import (
    ComplaintRegistrationForm, 
    ComplaintStatusUpdateForm, 
    ComplaintAssignmentForm, 
    ComplaintPriorityUpdateForm,
    CategoryForm,
    SubCategoryForm
)
from .services import register_complaint, generate_complaint_receipt_pdf
from accounts.decorators import citizen_required, staff_required, admin_required
from audit.services import log_activity
from notifications.services import send_notification

@login_required
def complaint_create(request):
    """Citizen complaint registration with attachments and geo-coordinates."""
    if request.method == 'POST':
        form = ComplaintRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            files = request.FILES.getlist('attachments')

            complaint = register_complaint(request.user, data, files)

            # Handle multiple attachment uploads
            for f in files:
                ComplaintAttachment.objects.create(
                    complaint=complaint,
                    file=f
                )

            log_activity(
                user=request.user,
                action='CREATE',
                description=f"Created complaint {complaint.complaint_id}: {complaint.title}",
                complaint=complaint,
                request=request
            )

            messages.success(request, f"Complaint registered successfully with ID: {complaint.complaint_id}")
            return redirect('complaints:receipt', complaint_id=complaint.complaint_id)
    else:
        initial_cat = request.GET.get('category')
        initial = {'category': initial_cat} if initial_cat else {}
        form = ComplaintRegistrationForm(initial=initial)

    return render(request, 'complaints/create.html', {'form': form})


def complaint_track_public(request):
    """Public tracking page accessible without login."""
    complaint_id = request.GET.get('complaint_id', '').strip().upper()
    complaint = None
    searched = False

    if complaint_id:
        searched = True
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()

    return render(request, 'complaints/track.html', {
        'complaint': complaint,
        'complaint_id': complaint_id,
        'searched': searched
    })


@login_required
def complaint_list(request):
    """Role-aware listing with advanced search, multi-criteria filtering, and sorting."""
    user = request.user
    queryset = Complaint.objects.select_related('user', 'category', 'department', 'assigned_staff').all()

    # Role-based restriction
    if user.role == 'CITIZEN':
        queryset = queryset.filter(user=user)
    elif user.role == 'STAFF':
        # Field officer views assigned complaints or unassigned department complaints
        dept = getattr(user, 'staff_profile', None) and user.staff_profile.department
        if dept:
            queryset = queryset.filter(Q(assigned_staff=user) | Q(department=dept, assigned_staff__isnull=True))
        else:
            queryset = queryset.filter(assigned_staff=user)

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(complaint_id__icontains=q) |
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location_address__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

    # Filter by Status
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Filter by Priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)

    # Filter by Category
    category_filter = request.GET.get('category')
    if category_filter:
        queryset = queryset.filter(category_id=category_filter)

    # Filter by Department
    department_filter = request.GET.get('department')
    if department_filter:
        queryset = queryset.filter(department_id=department_filter)

    # Filter by Overdue / Escalated
    overdue_filter = request.GET.get('overdue')
    if overdue_filter == '1':
        queryset = queryset.filter(due_date__lt=timezone.now()).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED'])

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-priority', 'priority', 'due_date', '-due_date', 'status']
    if sort_by in valid_sorts:
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'departments': departments,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_category': category_filter,
        'current_department': department_filter,
        'current_sort': sort_by,
        'query': q,
    }
    return render(request, 'complaints/list.html', context)


@login_required
def complaint_detail(request, complaint_id):
    """Comprehensive Complaint Overview with timelines, attachments, messages, and resolution."""
    user = request.user
    complaint = get_object_or_404(
        Complaint.objects.select_related('user', 'category', 'subcategory', 'department', 'assigned_staff'),
        complaint_id=complaint_id
    )

    # Permission check: Citizen can only view own complaint
    if user.role == 'CITIZEN' and complaint.user != user:
        messages.error(request, "You do not have authorization to view this complaint.")
        return redirect('complaints:list')

    attachments = complaint.attachments.all()
    history_logs = complaint.history_logs.select_related('changed_by').all().order_by('created_at')
    
    # Filter messages based on internal flag
    messages_query = complaint.discussion_messages.select_related('sender').all()
    if user.role == 'CITIZEN':
        messages_query = messages_query.filter(is_internal=False)

    resolution = getattr(complaint, 'resolution', None)
    feedback = getattr(complaint, 'feedback', None)

    status_form = ComplaintStatusUpdateForm(initial={'status': complaint.status})
    assign_form = ComplaintAssignmentForm(initial={'department': complaint.department, 'assigned_staff': complaint.assigned_staff})
    priority_form = ComplaintPriorityUpdateForm(initial={'priority': complaint.priority})

    context = {
        'complaint': complaint,
        'attachments': attachments,
        'history_logs': history_logs,
        'discussion_messages': messages_query,
        'resolution': resolution,
        'feedback': feedback,
        'status_form': status_form,
        'assign_form': assign_form,
        'priority_form': priority_form,
        'can_manage': user.role in ['STAFF', 'ADMIN'] or user.is_superuser,
        'can_assign': user.role == 'ADMIN' or user.is_superuser or (user.role == 'STAFF' and complaint.department and complaint.department.head_of_department == user),
    }
    return render(request, 'complaints/detail.html', context)


@login_required
def complaint_receipt_view(request, complaint_id):
    """View acknowledgment receipt on screen."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.user.role == 'CITIZEN' and complaint.user != request.user:
        messages.error(request, "Unauthorized access to receipt.")
        return redirect('dashboard:index')

    return render(request, 'complaints/receipt.html', {'complaint': complaint})


@login_required
def complaint_receipt_pdf_download(request, complaint_id):
    """Download official complaint receipt as PDF."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.user.role == 'CITIZEN' and complaint.user != request.user:
        return HttpResponse("Unauthorized", status=403)

    pdf_buffer = generate_complaint_receipt_pdf(complaint)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ResolveNow_Receipt_{complaint.complaint_id}.pdf"'
    return response


@login_required
def complaint_status_update(request, complaint_id):
    """Process status change with audit trail and notifications."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if not (request.user.role in ['STAFF', 'ADMIN'] or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ComplaintStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            remarks = form.cleaned_data['remarks']
            prev_status = complaint.status

            if new_status != prev_status:
                complaint.status = new_status
                if new_status in ['RESOLVED', 'CLOSED']:
                    complaint.closed_at = timezone.now()
                complaint.save()

                ComplaintHistory.objects.create(
                    complaint=complaint,
                    previous_status=prev_status,
                    new_status=new_status,
                    changed_by=request.user,
                    remarks=remarks
                )

                log_activity(
                    user=request.user,
                    action='STATUS_CHANGE',
                    description=f"Status changed from {prev_status} to {new_status}: {remarks}",
                    complaint=complaint,
                    request=request
                )

                # Notify citizen
                detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
                send_notification(
                    user=complaint.user,
                    title=f"Complaint Status Updated: {complaint.get_status_display()}",
                    message=f"Your complaint [{complaint.complaint_id}] status is now: {complaint.get_status_display()}. Remarks: {remarks}",
                    link=detail_url
                )

                messages.success(request, f"Status updated to {complaint.get_status_display()}.")
    return redirect('complaints:detail', complaint_id=complaint.complaint_id)


@login_required
def complaint_assign(request, complaint_id):
    """Assign or reassign complaint to department and field officer."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or (complaint.department and complaint.department.head_of_department == request.user)):
        messages.error(request, "Permission denied.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ComplaintAssignmentForm(request.POST)
        if form.is_valid():
            dept = form.cleaned_data['department']
            staff = form.cleaned_data['assigned_staff']
            remarks = form.cleaned_data['remarks']

            old_staff = complaint.assigned_staff
            complaint.department = dept
            complaint.assigned_staff = staff
            if complaint.status in ['SUBMITTED', 'UNDER_REVIEW']:
                complaint.status = 'ASSIGNED'
            complaint.save()

            history_msg = f"Assigned to {staff.get_full_name() or staff.username} ({dept.name})." if staff else f"Department set to {dept.name}."
            if remarks:
                history_msg += f" Note: {remarks}"

            ComplaintHistory.objects.create(
                complaint=complaint,
                previous_status=complaint.status,
                new_status=complaint.status,
                changed_by=request.user,
                remarks=history_msg
            )

            log_activity(
                user=request.user,
                action='ASSIGN',
                description=f"Assignment updated: {history_msg}",
                complaint=complaint,
                request=request
            )

            if staff and staff != old_staff:
                detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
                send_notification(
                    user=staff,
                    title="Complaint Assigned",
                    message=f"You have been assigned complaint [{complaint.complaint_id}]: '{complaint.title}'.",
                    link=detail_url
                )

            messages.success(request, "Assignment updated successfully.")
    return redirect('complaints:detail', complaint_id=complaint.complaint_id)


@login_required
def complaint_priority_update(request, complaint_id):
    """Adjust priority level."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if not (request.user.role == 'ADMIN' or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('complaints:detail', complaint_id=complaint.complaint_id)

    if request.method == 'POST':
        form = ComplaintPriorityUpdateForm(request.POST)
        if form.is_valid():
            old_p = complaint.priority
            new_p = form.cleaned_data['priority']
            remarks = form.cleaned_data['remarks']

            complaint.priority = new_p
            complaint.save()

            ComplaintHistory.objects.create(
                complaint=complaint,
                previous_status=complaint.status,
                new_status=complaint.status,
                changed_by=request.user,
                remarks=f"Priority changed from {old_p} to {new_p}. Reason: {remarks}"
            )

            log_activity(
                user=request.user,
                action='UPDATE',
                description=f"Priority updated from {old_p} to {new_p}: {remarks}",
                complaint=complaint,
                request=request
            )

            messages.success(request, f"Priority adjusted to {complaint.get_priority_display()}.")
    return redirect('complaints:detail', complaint_id=complaint.complaint_id)


def subcategories_ajax(request):
    """AJAX endpoint to dynamically fetch subcategories for category selection."""
    category_id = request.GET.get('category_id')
    if category_id:
        subcats = SubCategory.objects.filter(category_id=category_id, is_active=True).values('id', 'name')
        return JsonResponse(list(subcats), safe=False)
    return JsonResponse([], safe=False)


@admin_required
def category_list(request):
    categories = Category.objects.select_related('department').prefetch_related('subcategories').all()
    return render(request, 'complaints/category_list.html', {'categories': categories})


@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created.")
            return redirect('complaints:category_list')
    else:
        form = CategoryForm()
    return render(request, 'complaints/category_form.html', {'form': form, 'title': 'Create Category'})


@admin_required
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{cat.name}' updated.")
            return redirect('complaints:category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'complaints/category_form.html', {'form': form, 'title': f'Edit Category: {cat.name}', 'category': cat})


@admin_required
def subcategory_create(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            subcat = form.save(commit=False)
            subcat.category = category
            subcat.save()
            messages.success(request, f"Subcategory '{subcat.name}' added to {category.name}.")
            return redirect('complaints:category_list')
    else:
        form = SubCategoryForm(initial={'category': category})
    return render(request, 'complaints/subcategory_form.html', {'form': form, 'category': category})
