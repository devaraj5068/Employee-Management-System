from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint, Category, STATUS_CHOICES, PRIORITY_CHOICES
from departments.models import Department

@login_required
def complaint_map_view(request):
    """
    Renders the city-wide interactive geospatial map view with filters
    for Status, Priority, Category, and Department.
    """
    categories = Category.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    return render(request, 'location/map_view.html', {
        'categories': categories,
        'departments': departments,
        'status_choices': STATUS_CHOICES,
        'priority_choices': PRIORITY_CHOICES,
    })


@login_required
def complaint_markers_api(request):
    """
    JSON API returning complaint geolocation markers with metadata for Google Maps rendering.
    Safe and sanitized: never returns passwords, tokens, or private personal citizen data.
    """
    queryset = Complaint.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('category', 'department', 'assigned_staff')

    # Apply filters if provided
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    priority = request.GET.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)

    category_id = request.GET.get('category')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    department_id = request.GET.get('department')
    if department_id:
        queryset = queryset.filter(department_id=department_id)

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(complaint_id__icontains=query) |
            Q(title__icontains=query) |
            Q(location_address__icontains=query)
        )

    markers = []
    for c in queryset[:300]:
        try:
            lat = float(c.latitude)
            lng = float(c.longitude)
        except (ValueError, TypeError):
            continue

        # Basic bounding sanity check
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            continue

        markers.append({
            'id': c.complaint_id,
            'title': c.title,
            'lat': lat,
            'lng': lng,
            'latitude': lat,
            'longitude': lng,
            'priority': c.priority,
            'priority_display': c.get_priority_display(),
            'status': c.get_status_display(),
            'status_code': c.status,
            'category': c.category.name if c.category else 'General',
            'department': c.department.name if c.department else 'Unassigned',
            'assigned_officer': (c.assigned_staff.get_full_name() or c.assigned_staff.username) if c.assigned_staff else 'Unassigned',
            'address': c.location_address or "Location coordinates recorded",
            'date': c.created_at.strftime('%Y-%m-%d'),
            'url': reverse('complaints:detail', kwargs={'complaint_id': c.complaint_id})
        })

    return JsonResponse({'markers': markers, 'count': len(markers)})
