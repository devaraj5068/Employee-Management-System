import logging
from django.db.models import Count, Q
from .models import StaffProfile

logger = logging.getLogger(__name__)

def auto_assign_complaint(complaint):
    """
    Intelligent workload-balanced automatic assignment engine:
    1. Looks at the complaint's department.
    2. Identifies all available active staff members in that department.
    3. Finds the staff member with the lowest number of currently active tickets.
    4. Ensures they haven't exceeded max_active_capacity.
    5. Assigns the complaint and updates status to 'ASSIGNED'.
    """
    if not complaint.department:
        return None

    # Get available staff profiles in this department
    available_staff = StaffProfile.objects.filter(
        department=complaint.department,
        is_available=True,
        user__is_active=True,
        user__account_status='ACTIVE'
    )

    if not available_staff.exists():
        logger.info(f"No available staff found for department {complaint.department.name}")
        return None

    # Sort by active workload
    candidates = []
    for sp in available_staff:
        if sp.can_take_new_complaint:
            candidates.append((sp.current_active_complaints_count, sp))

    if not candidates:
        logger.warning(f"All staff in department {complaint.department.name} are at full capacity.")
        return None

    # Sort candidates by current workload ascending
    candidates.sort(key=lambda x: x[0])
    selected_staff_profile = candidates[0][1]
    selected_user = selected_staff_profile.user

    # Assign
    complaint.assigned_staff = selected_user
    if complaint.status in ['SUBMITTED', 'UNDER_REVIEW']:
        complaint.status = 'ASSIGNED'
    complaint.save(update_fields=['assigned_staff', 'status', 'updated_at'])

    return selected_user
