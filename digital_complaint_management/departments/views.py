from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Department
from .forms import DepartmentForm

@admin_required
def department_list(request):
    departments = Department.objects.all().select_related('head_of_department').prefetch_related('staff_members')
    return render(request, 'departments/list.html', {'departments': departments})


@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully!")
            return redirect('departments:list')
    else:
        form = DepartmentForm()
    return render(request, 'departments/form.html', {'form': form, 'title': 'Create New Department'})


@admin_required
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully.")
            return redirect('departments:list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'departments/form.html', {'form': form, 'title': f'Edit Department: {dept.name}', 'dept': dept})


@admin_required
def department_toggle_status(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.is_active = not dept.is_active
    dept.save()
    status_str = "activated" if dept.is_active else "deactivated"
    messages.info(request, f"Department '{dept.name}' has been {status_str}.")
    return redirect('departments:list')
