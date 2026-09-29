import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from complaints.models import Complaint, Category, PRIORITY_CHOICES, STATUS_CHOICES
from departments.models import Department
from staff.models import StaffProfile
from audit.models import ActivityLog

@login_required
def index(request):
    """Entry point: Dispatches user to their designated dashboard."""
    role = request.user.role
    if role == 'ADMIN' or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    elif role == 'STAFF':
        return redirect('dashboard:staff_dashboard')
    else:
        return redirect('dashboard:user_dashboard')


@login_required
def user_dashboard(request):
    """Citizen dashboard with self-service KPIs, recent history, and quick actions."""
    complaints = Complaint.objects.filter(user=request.user).select_related('category', 'department')

    total_count = complaints.count()
    pending_count = complaints.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count()
    in_progress_count = complaints.filter(status__in=['ASSIGNED', 'IN_PROGRESS', 'ON_HOLD']).count()
    resolved_count = complaints.filter(status='RESOLVED').count()
    closed_count = complaints.filter(status='CLOSED').count()
    reopened_count = complaints.filter(status='REOPENED').count()

    recent_complaints = complaints[:8]

    context = {
        'total_count': total_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'reopened_count': reopened_count,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def staff_dashboard(request):
    """Field officer dashboard with assigned tickets, urgent alerts, and workload."""
    user = request.user
    assigned_query = Complaint.objects.filter(assigned_staff=user).select_related('category', 'department', 'user')

    total_assigned = assigned_query.count()
    pending_assigned = assigned_query.filter(status__in=['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED']).count()
    in_progress = assigned_query.filter(status='IN_PROGRESS').count()
    resolved_count = assigned_query.filter(status__in=['RESOLVED', 'CLOSED']).count()
    critical_count = assigned_query.filter(priority='CRITICAL').exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()
    overdue_count = assigned_query.filter(due_date__lt=timezone.now()).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()

    # Staff profile info
    profile = getattr(user, 'staff_profile', None)
    workload_pct = profile.workload_percentage if profile else 50

    recent_assigned = assigned_query.exclude(status__in=['RESOLVED', 'CLOSED'])[:10]

    context = {
        'total_assigned': total_assigned,
        'pending_assigned': pending_assigned,
        'in_progress': in_progress,
        'resolved_count': resolved_count,
        'critical_count': critical_count,
        'overdue_count': overdue_count,
        'workload_pct': workload_pct,
        'recent_assigned': recent_assigned,
        'profile': profile,
    }
    return render(request, 'dashboard/staff_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Executive administrative control center with analytics, SLA metrics, and charts."""
    if not (request.user.role == 'ADMIN' or request.user.is_superuser):
        return redirect('dashboard:index')

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Aggregations
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED']).count()
    submitted_count = Complaint.objects.filter(status='SUBMITTED').count()
    under_review_count = Complaint.objects.filter(status='UNDER_REVIEW').count()
    in_progress_count = Complaint.objects.filter(status='IN_PROGRESS').count()
    resolved_count = Complaint.objects.filter(status='RESOLVED').count()
    closed_count = Complaint.objects.filter(status='CLOSED').count()
    rejected_count = Complaint.objects.filter(status='REJECTED').count()
    reopened_count = Complaint.objects.filter(status='REOPENED').count()
    critical_count = Complaint.objects.filter(priority='CRITICAL').exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()
    today_count = Complaint.objects.filter(created_at__gte=today_start).count()
    overdue_count = Complaint.objects.filter(due_date__lt=now).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()

    # Chart 1: Status Distribution
    status_counts = dict(Complaint.objects.values_list('status').annotate(total=Count('id')))
    chart_status_labels = [label for key, label in STATUS_CHOICES]
    chart_status_data = [status_counts.get(key, 0) for key, label in STATUS_CHOICES]

    # Chart 2: Priority Distribution
    priority_counts = dict(Complaint.objects.values_list('priority').annotate(total=Count('id')))
    chart_priority_labels = ['Low', 'Medium', 'High', 'Critical']
    chart_priority_data = [
        priority_counts.get('LOW', 0),
        priority_counts.get('MEDIUM', 0),
        priority_counts.get('HIGH', 0),
        priority_counts.get('CRITICAL', 0),
    ]

    # Chart 3: Category-wise Distribution
    cat_qs = Category.objects.annotate(comp_count=Count('complaints')).order_by('-comp_count')[:7]
    chart_cat_labels = [c.name for c in cat_qs]
    chart_cat_data = [c.comp_count for c in cat_qs]

    # Chart 4: Department-wise Distribution
    dept_qs = Department.objects.annotate(comp_count=Count('complaints')).order_by('-comp_count')[:6]
    chart_dept_labels = [d.name for d in dept_qs]
    chart_dept_data = [d.comp_count for d in dept_qs]

    # Chart 5: Last 6 Months Trend
    trend_labels = []
    trend_data = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=i * 30)
        m_label = month_date.strftime('%b %Y')
        m_count = Complaint.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        trend_labels.append(m_label)
        trend_data.append(m_count)

    # Recent Alerts & Tables
    critical_complaints = Complaint.objects.filter(
        Q(priority='CRITICAL') | Q(is_escalated=True)
    ).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).select_related('department', 'assigned_staff')[:6]

    recent_complaints = Complaint.objects.select_related('category', 'department', 'user').all()[:8]
    recent_activities = ActivityLog.objects.select_related('user', 'complaint').all()[:8]
    staff_profiles = StaffProfile.objects.select_related('user', 'department').all()[:6]

    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'submitted_count': submitted_count,
        'under_review_count': under_review_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'rejected_count': rejected_count,
        'reopened_count': reopened_count,
        'critical_count': critical_count,
        'today_count': today_count,
        'overdue_count': overdue_count,

        # Charts JSON
        'chart_status_labels_json': json.dumps(chart_status_labels),
        'chart_status_data_json': json.dumps(chart_status_data),
        'chart_priority_labels_json': json.dumps(chart_priority_labels),
        'chart_priority_data_json': json.dumps(chart_priority_data),
        'chart_cat_labels_json': json.dumps(chart_cat_labels),
        'chart_cat_data_json': json.dumps(chart_cat_data),
        'chart_dept_labels_json': json.dumps(chart_dept_labels),
        'chart_dept_data_json': json.dumps(chart_dept_data),
        'chart_trend_labels_json': json.dumps(trend_labels),
        'chart_trend_data_json': json.dumps(trend_data),

        'critical_complaints': critical_complaints,
        'recent_complaints': recent_complaints,
        'recent_activities': recent_activities,
        'staff_profiles': staff_profiles,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
