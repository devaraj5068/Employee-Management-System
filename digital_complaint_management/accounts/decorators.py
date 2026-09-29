from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def citizen_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.role == 'CITIZEN' or request.user.is_superuser):
            messages.error(request, "Access restricted: This area is reserved for Citizens.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.role in ['STAFF', 'ADMIN'] or request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Access restricted: Only Officers and Staff can view this resource.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.role == 'ADMIN' or request.user.is_superuser):
            messages.error(request, "Access restricted: Administrative privileges required.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
