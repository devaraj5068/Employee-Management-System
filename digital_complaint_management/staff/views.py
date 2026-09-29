from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import admin_required, staff_required
from .models import StaffProfile
from .forms import StaffCreationForm, StaffProfileUpdateForm
from complaints.models import Complaint

@admin_required
def staff_list(request):
    profiles = StaffProfile.objects.select_related('user', 'department').all()
    return render(request, 'staff/list.html', {'profiles': profiles})


@admin_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f"Officer account created for {staff.user.get_full_name()} ({staff.employee_id})")
            return redirect('staff:list')
    else:
        form = StaffCreationForm()
    return render(request, 'staff/form.html', {'form': form, 'title': 'Register New Staff Officer'})


@admin_required
def staff_update(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        form = StaffProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Staff record for {profile.user.get_full_name()} updated successfully.")
            return redirect('staff:list')
    else:
        form = StaffProfileUpdateForm(instance=profile)
    return render(request, 'staff/form.html', {'form': form, 'title': f'Edit Officer Profile: {profile.user.get_full_name()}', 'profile': profile})


@admin_required
def staff_workload_dashboard(request):
    profiles = StaffProfile.objects.select_related('user', 'department').all()
    workload_data = []
    for sp in profiles:
        active_cnt = sp.current_active_complaints_count
        resolved_cnt = Complaint.objects.filter(assigned_staff=sp.user, status__in=['RESOLVED', 'CLOSED']).count()
        overdue_cnt = Complaint.objects.filter(assigned_staff=sp.user, is_escalated=True).exclude(status__in=['RESOLVED', 'CLOSED', 'REJECTED']).count()
        workload_data.append({
            'profile': sp,
            'active_count': active_cnt,
            'resolved_count': resolved_cnt,
            'overdue_count': overdue_cnt,
            'pct': sp.workload_percentage
        })
    return render(request, 'staff/workload.html', {'workload_data': workload_data})
