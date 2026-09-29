from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ActivityLog, SystemConfiguration, ACTION_CHOICES
from accounts.decorators import admin_required

@admin_required
def audit_log_list(request):
    logs = ActivityLog.objects.select_related('user', 'complaint').all()

    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    q = request.GET.get('q')
    if q:
        logs = logs.filter(
            Q(description__icontains=q) |
            Q(user__username__icontains=q) |
            Q(complaint__complaint_id__icontains=q) |
            Q(ip_address__icontains=q)
        )

    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'audit/audit_logs.html', {
        'page_obj': page_obj,
        'action_choices': ACTION_CHOICES,
        'current_action': action,
        'query': q,
    })


@admin_required
def system_config_view(request):
    configs = SystemConfiguration.objects.all()

    if request.method == 'POST':
        for cfg in configs:
            val = request.POST.get(f"config_{cfg.id}")
            if val is not None and val != cfg.value:
                cfg.value = val.strip()
                cfg.save()
        messages.success(request, "System configurations updated successfully.")
        return redirect('audit:system_config')

    return render(request, 'audit/system_config.html', {'configs': configs})
