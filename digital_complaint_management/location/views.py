from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint, Category
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
    })


@login_required
def complaint_markers_api(request):
    """
    JSON API returning complaint geolocation markers with metadata for Leaflet rendering.
    """
    queryset = Complaint.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('category', 'department')

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

    markers = []
    for c in queryset[:200]:
        markers.append({
            'id': c.complaint_id,
            'title': c.title,
            'lat': float(c.latitude),
            'lng': float(c.longitude),
            'priority': c.priority,
            'status': c.get_status_display(),
            'category': c.category.name,
            'address': c.location_address or "Location coordinates recorded",
            'date': c.created_at.strftime('%Y-%m-%d'),
            'url': f"/complaints/{c.complaint_id}/"
        })

    return JsonResponse({'markers': markers})
