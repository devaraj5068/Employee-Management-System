from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    notifs = request.user.notifications.all()
    return render(request, 'notifications/list.html', {'notifications': notifs})


@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')


@login_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    messages.info(request, "Notification deleted.")
    return redirect('notifications:list')
