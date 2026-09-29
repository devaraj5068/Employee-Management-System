import io
import os
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from django.urls import reverse
from .models import Complaint, ComplaintHistory
from staff.services import auto_assign_complaint
from notifications.services import send_notification

def calculate_due_date(priority):
    """Calculate SLA resolution deadline based on priority."""
    now = timezone.now()
    hours_map = {
        'CRITICAL': 24,    # 1 day
        'HIGH': 48,        # 2 days
        'MEDIUM': 96,      # 4 days
        'LOW': 168,        # 7 days
    }
    hours = hours_map.get(priority, 96)
    return now + timedelta(hours=hours)


def register_complaint(user, data, files):
    """
    Service to register a new complaint:
    - Auto-generates ID (RN-YYYY-XXXXXX)
    - Resolves Department from Category
    - Calculates SLA due date
    - Saves attachments
    - Creates initial ComplaintHistory record
    - Auto-assigns to staff in department if auto-assign is enabled
    - Triggers notifications to Citizen and Department
    """
    category = data.get('category')
    department = category.department if category else None
    priority = data.get('priority') or (category.default_priority if category else 'MEDIUM')
    due_date = calculate_due_date(priority)

    complaint = Complaint.objects.create(
        complaint_id=Complaint.generate_complaint_id(),
        user=user,
        title=data.get('title'),
        description=data.get('description'),
        category=category,
        subcategory=data.get('subcategory'),
        priority=priority,
        department=department,
        status='SUBMITTED',
        location_address=data.get('location_address', ''),
        latitude=data.get('latitude') or None,
        longitude=data.get('longitude') or None,
        due_date=due_date
    )

    # Initial history record
    ComplaintHistory.objects.create(
        complaint=complaint,
        previous_status=None,
        new_status='SUBMITTED',
        changed_by=user,
        remarks="Complaint registered online via citizen portal."
    )

    # Try automatic assignment to available officer
    assigned_officer = auto_assign_complaint(complaint)
    if assigned_officer:
        ComplaintHistory.objects.create(
            complaint=complaint,
            previous_status='SUBMITTED',
            new_status='ASSIGNED',
            changed_by=None,
            remarks=f"Automatically assigned to field officer: {assigned_officer.get_full_name() or assigned_officer.username}"
        )
        detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
        send_notification(
            user=assigned_officer,
            title="New Complaint Assigned",
            message=f"Complaint [{complaint.complaint_id}] '{complaint.title}' has been assigned to your queue.",
            link=detail_url
        )

    # Notify Citizen
    detail_url = reverse('complaints:detail', kwargs={'complaint_id': complaint.complaint_id})
    send_notification(
        user=user,
        title="Complaint Submitted Successfully",
        message=f"Your complaint has been registered with ID: {complaint.complaint_id}. Estimated resolution by {complaint.due_date:%b %d, %Y}.",
        link=detail_url
    )

    return complaint


def generate_complaint_receipt_pdf(complaint):
    """
    Generates an official PDF receipt for a registered complaint using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d6efd'),
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'ReceiptSubtitle',
        parent=normal_style,
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#6c757d'),
        alignment=1
    )

    badge_style = ParagraphStyle(
        'ReceiptBadge',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#198754'),
        alignment=1
    )

    elements = []

    # Header
    elements.append(Paragraph("ResolveNow", title_style))
    elements.append(Paragraph("Citizen Online Complaint Resolution System", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0d6efd'), spaceAfter=15))

    elements.append(Paragraph("OFFICIAL COMPLAINT ACKNOWLEDGMENT RECEIPT", badge_style))
    elements.append(Spacer(1, 15))

    # Complaint Table
    table_data = [
        [Paragraph("<b>Complaint ID:</b>", normal_style), Paragraph(f"<b>{complaint.complaint_id}</b>", normal_style)],
        [Paragraph("<b>Subject / Title:</b>", normal_style), Paragraph(complaint.title, normal_style)],
        [Paragraph("<b>Category:</b>", normal_style), Paragraph(f"{complaint.category.name} ({complaint.subcategory.name if complaint.subcategory else 'General'})", normal_style)],
        [Paragraph("<b>Department:</b>", normal_style), Paragraph(complaint.department.name if complaint.department else "General Services", normal_style)],
        [Paragraph("<b>Priority:</b>", normal_style), Paragraph(f"{complaint.get_priority_display()}", normal_style)],
        [Paragraph("<b>Current Status:</b>", normal_style), Paragraph(f"{complaint.get_status_display()}", normal_style)],
        [Paragraph("<b>Submitted By:</b>", normal_style), Paragraph(f"{complaint.user.get_full_name() or complaint.user.username} ({complaint.user.email})", normal_style)],
        [Paragraph("<b>Submission Date:</b>", normal_style), Paragraph(f"{complaint.created_at:%Y-%m-%d %H:%M:%S}", normal_style)],
        [Paragraph("<b>Target Resolution SLA:</b>", normal_style), Paragraph(f"{complaint.due_date:%Y-%m-%d %H:%M:%S}" if complaint.due_date else "Standard SLA", normal_style)],
        [Paragraph("<b>Location / Address:</b>", normal_style), Paragraph(complaint.location_address or "Not Specified", normal_style)],
        [Paragraph("<b>Coordinates:</b>", normal_style), Paragraph(f"Lat: {complaint.latitude}, Long: {complaint.longitude}" if complaint.latitude else "N/A", normal_style)],
        [Paragraph("<b>Assigned Officer:</b>", normal_style), Paragraph(complaint.assigned_staff.get_full_name() if complaint.assigned_staff else "Under Department Review", normal_style)],
    ]

    t = Table(table_data, colWidths=[160, 370])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    # Description Section
    elements.append(Paragraph("<b>Complaint Description:</b>", normal_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(complaint.description, normal_style))
    elements.append(Spacer(1, 20))

    # Footer note
    footer_text = (
        "<i>Note: This is a system-generated acknowledgment receipt. You can track live status updates at any time "
        f"by searching Complaint ID <b>{complaint.complaint_id}</b> on the ResolveNow portal or visiting your user dashboard.</i>"
    )
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=10))
    elements.append(Paragraph(footer_text, ParagraphStyle('ReceiptFooter', parent=normal_style, fontSize=9, textColor=colors.HexColor('#6c757d'))))

    doc.build(elements)
    buffer.seek(0)
    return buffer
