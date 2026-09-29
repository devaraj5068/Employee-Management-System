import io
import csv
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from complaints.models import Complaint, Category
from departments.models import Department
from accounts.decorators import admin_required

def get_filtered_complaints(request):
    """Utility to filter complaints based on requested timeframe and department."""
    now = timezone.now()
    period = request.GET.get('period', 'monthly')
    dept_id = request.GET.get('department')

    qs = Complaint.objects.select_related('category', 'department', 'assigned_staff', 'user')

    if period == 'daily':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        qs = qs.filter(created_at__gte=start)
    elif period == 'weekly':
        start = now - timedelta(days=7)
        qs = qs.filter(created_at__gte=start)
    elif period == 'monthly':
        start = now - timedelta(days=30)
        qs = qs.filter(created_at__gte=start)
    elif period == 'yearly':
        start = now - timedelta(days=365)
        qs = qs.filter(created_at__gte=start)

    if dept_id:
        qs = qs.filter(department_id=dept_id)

    return qs, period


@admin_required
def report_analytics_view(request):
    complaints, period = get_filtered_complaints(request)
    departments = Department.objects.filter(is_active=True)

    total = complaints.count()
    resolved = complaints.filter(status__in=['RESOLVED', 'CLOSED']).count()
    pending = complaints.filter(status__in=['SUBMITTED', 'UNDER_REVIEW', 'ASSIGNED', 'IN_PROGRESS', 'ON_HOLD']).count()
    escalated = complaints.filter(is_escalated=True).count()
    resolution_rate = round((resolved / total * 100)) if total > 0 else 0

    dept_stats = complaints.values('department__name').annotate(
        total=Count('id'),
        resolved_cnt=Count('id', filter=Q(status__in=['RESOLVED', 'CLOSED'])),
        escalated_cnt=Count('id', filter=Q(is_escalated=True))
    ).order_by('-total')

    context = {
        'complaints': complaints[:25],
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'escalated': escalated,
        'resolution_rate': resolution_rate,
        'dept_stats': dept_stats,
        'departments': departments,
        'current_period': period,
        'current_dept': request.GET.get('department', ''),
    }
    return render(request, 'reports/analytics.html', context)


@admin_required
def export_pdf_report(request):
    complaints, period = get_filtered_complaints(request)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0d6efd'),
        alignment=1
    )

    elements = []
    elements.append(Paragraph("ResolveNow - Online Complaint Resolution Platform", title_style))
    elements.append(Paragraph(f"<b>Executive Analytics & Compliance Report</b> | Period: {period.capitalize()} | Generated: {timezone.now():%Y-%m-%d %H:%M}", ParagraphStyle('Sub', parent=normal_style, alignment=1, textColor=colors.HexColor('#555555'))))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d6efd'), spaceAfter=15))

    # Summary Stats Table
    total = complaints.count()
    resolved = complaints.filter(status__in=['RESOLVED', 'CLOSED']).count()
    pending = total - resolved
    escalated = complaints.filter(is_escalated=True).count()

    summary_data = [
        ["Total Registered", "Resolved / Closed", "Pending Active", "Escalated Breaches"],
        [str(total), str(resolved), str(pending), str(escalated)]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # Detailed Complaints Table
    table_rows = [["ID", "Title", "Category", "Department", "Priority", "Status", "Created", "Assigned Officer"]]
    for c in complaints[:80]:
        table_rows.append([
            c.complaint_id,
            c.title[:24] + "..." if len(c.title) > 24 else c.title,
            c.category.name[:16],
            c.department.name[:18] if c.department else "-",
            c.priority,
            c.get_status_display(),
            c.created_at.strftime('%Y-%m-%d'),
            c.assigned_staff.username if c.assigned_staff else "Unassigned"
        ])

    table = Table(table_rows, colWidths=[90, 130, 95, 110, 65, 80, 75, 85])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ResolveNow_Report_{period}_{timezone.now():%Y%m%d}.pdf"'
    return response


@admin_required
def export_excel_report(request):
    complaints, period = get_filtered_complaints(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Complaints Report"

    # Styling
    header_fill = PatternFill(start_color="0D6EFD", end_color="0D6EFD", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Arial", size=14, bold=True, color="0D6EFD")
    border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    # Title
    ws.merge_cells('A1:I1')
    ws['A1'] = f"ResolveNow Complaints Report - {period.capitalize()} ({timezone.now():%Y-%m-%d})"
    ws['A1'].font = title_font
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30

    # Headers
    headers = [
        "Complaint ID", "Title", "Category", "Subcategory", "Department",
        "Priority", "Status", "Citizen Name", "Citizen Email",
        "Assigned Officer", "Location", "Submission Date", "SLA Deadline", "Is Escalated"
    ]
    ws.append([])  # blank row
    ws.append(headers)

    header_row_idx = 3
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=header_row_idx, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Data Rows
    for c in complaints:
        ws.append([
            c.complaint_id,
            c.title,
            c.category.name,
            c.subcategory.name if c.subcategory else "",
            c.department.name if c.department else "",
            c.priority,
            c.get_status_display(),
            c.user.get_full_name() or c.user.username,
            c.user.email,
            c.assigned_staff.get_full_name() if c.assigned_staff else "Unassigned",
            c.location_address or "",
            c.created_at.strftime('%Y-%m-%d %H:%M'),
            c.due_date.strftime('%Y-%m-%d %H:%M') if c.due_date else "",
            "YES" if c.is_escalated else "NO"
        ])

    # Auto-adjust column widths
    for col_idx, col in enumerate(ws.columns, start=1):
        max_len = 0
        col_letter = get_column_letter(col_idx)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="ResolveNow_Report_{period}_{timezone.now():%Y%m%d}.xlsx"'
    return response


@admin_required
def export_csv_report(request):
    complaints, period = get_filtered_complaints(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ResolveNow_Report_{period}_{timezone.now():%Y%m%d}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Complaint ID", "Title", "Category", "Department", "Priority", 
        "Status", "Citizen Username", "Officer", "Address", "Created At", "Due Date", "Escalated"
    ])

    for c in complaints:
        writer.writerow([
            c.complaint_id,
            c.title,
            c.category.name,
            c.department.name if c.department else "",
            c.priority,
            c.status,
            c.user.username,
            c.assigned_staff.username if c.assigned_staff else "",
            c.location_address or "",
            c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            c.due_date.strftime('%Y-%m-%d %H:%M:%S') if c.due_date else "",
            "1" if c.is_escalated else "0"
        ])

    return response
