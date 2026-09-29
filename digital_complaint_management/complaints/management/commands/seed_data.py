from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import CustomUser
from departments.models import Department
from staff.models import StaffProfile
from complaints.models import Category, SubCategory, Complaint, ComplaintHistory
from resolutions.models import Resolution
from communication.models import ComplaintMessage
from feedback.models import ComplaintFeedback
from escalation.models import EscalationRule, EscalationLog
from audit.models import SystemConfiguration, ActivityLog

class Command(BaseCommand):
    help = "Seeds database with essential master data, demo roles, and sample realistic complaints."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Starting ResolveNow Database Seeding ---"))

        # 1. System Configurations
        configs = [
            ('PLATFORM_NAME', 'ResolveNow', 'Platform brand name'),
            ('PLATFORM_TAGLINE', 'Online Citizen Complaint Resolution Platform', 'Brand subtitle'),
            ('SUPPORT_EMAIL', 'support@resolvenow.org', 'Official citizen help email'),
            ('SUPPORT_PHONE', '1800-CIVIC-RESOLVE', 'Toll-free citizen helpdesk'),
            ('ALLOW_REOPEN_DAYS', '7', 'Days allowed after resolution for citizen to reopen'),
            ('AUTO_ASSIGNMENT_ENABLED', 'True', 'Enable smart workload-balanced staff assignment'),
        ]
        for k, v, d in configs:
            SystemConfiguration.objects.update_or_create(key=k, defaults={'value': v, 'description': d})
        self.stdout.write(self.style.SUCCESS("[OK] System configurations initialized."))

        # 2. SLA Escalation Rules
        sla_rules = [
            ('CRITICAL', 24, 6),
            ('HIGH', 48, 12),
            ('MEDIUM', 96, 24),
            ('LOW', 168, 48),
        ]
        for priority, hours, warn in sla_rules:
            EscalationRule.objects.update_or_create(
                priority=priority,
                defaults={
                    'resolution_deadline_hours': hours,
                    'level1_warning_hours': warn,
                    'escalation_level_2_target': 'DEPARTMENT_HEAD',
                    'escalation_level_3_target': 'ADMINISTRATOR',
                    'escalation_level_4_target': 'MUNICIPAL_COMMISSIONER'
                }
            )
        self.stdout.write(self.style.SUCCESS("[OK] SLA escalation rules configured."))

        # 3. User Accounts
        # Admin
        admin_user, _ = CustomUser.objects.update_or_create(
            username='admin',
            defaults={
                'email': 'admin@resolvenow.org',
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': 'ADMIN',
                'phone_number': '+91 9876543210',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'account_status': 'ACTIVE',
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Citizens
        john, _ = CustomUser.objects.update_or_create(
            username='citizen_john',
            defaults={
                'email': 'john.citizen@gmail.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'CITIZEN',
                'phone_number': '+91 9812345678',
                'address': '#42, Elm Street, Greenwood Colony',
                'is_verified': True,
                'account_status': 'ACTIVE',
            }
        )
        john.set_password('citizen123')
        john.save()

        sarah, _ = CustomUser.objects.update_or_create(
            username='citizen_sarah',
            defaults={
                'email': 'sarah.smith@gmail.com',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'role': 'CITIZEN',
                'phone_number': '+91 9812345679',
                'address': 'Flat 302, Sunrise Heights, Metro Boulevard',
                'is_verified': True,
                'account_status': 'ACTIVE',
            }
        )
        sarah.set_password('citizen123')
        sarah.save()

        self.stdout.write(self.style.SUCCESS("[OK] Admin and Citizen accounts seeded."))

        # 4. Departments
        depts_data = [
            ('ROADS', 'Roads & Bridges Infrastructure', 'Maintenance and repairs of public asphalt roads, signals, and bridges', 'roads@civic.gov'),
            ('WATER', 'Water Supply & Sewerage Board', 'Municipal drinking water pipeline distribution, pumps, and sewer drainage', 'water@civic.gov'),
            ('ELEC', 'Electricity & Power Distribution', 'Electrical sub-stations, transformers, street wiring, and high-tension cables', 'power@civic.gov'),
            ('SANI', 'Sanitation & Solid Waste Management', 'Garbage collection, public dustbins, road sweeping, and landfill disposal', 'sanitation@civic.gov'),
            ('LITE', 'Street Lighting & Urban Fixtures', 'Public road lighting, LED lamps, and illuminated junctions', 'lighting@civic.gov'),
            ('HLTH', 'Public Health & Drainage', 'Stormwater drains, mosquito abatement, manholes, and sanitation hygiene', 'health@civic.gov'),
            ('TRAN', 'Public Transport & Mobility', 'City buses, bus stops, pedestrian paths, and traffic coordination', 'transit@civic.gov'),
            ('GEN', 'General Administrative Services', 'Civic documentation, license verification, municipal property inspection', 'services@civic.gov'),
        ]
        dept_objs = {}
        for code, name, desc, email in depts_data:
            d, _ = Department.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'contact_email': email,
                    'head_of_department': admin_user,
                    'is_active': True
                }
            )
            dept_objs[code] = d

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(dept_objs)} Civic Departments created."))

        # 5. Field Officers / Staff
        staff_data = [
            ('officer_water', 'Robert', 'Taylor', 'water.officer@resolvenow.org', dept_objs['WATER'], 'Chief Water Inspector', 'EMP-WTR-01'),
            ('officer_roads', 'Vikram', 'Singh', 'roads.officer@resolvenow.org', dept_objs['ROADS'], 'Executive Highway Engineer', 'EMP-RDS-02'),
            ('officer_elec', 'Ananya', 'Sharma', 'elec.officer@resolvenow.org', dept_objs['ELEC'], 'Assistant Power Engineer', 'EMP-ELC-03'),
            ('officer_sani', 'Michael', 'Chang', 'sani.officer@resolvenow.org', dept_objs['SANI'], 'Sanitary Inspector', 'EMP-SAN-04'),
        ]
        staff_objs = {}
        for username, fname, lname, email, dept, designation, empid in staff_data:
            u, _ = CustomUser.objects.update_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'STAFF',
                    'phone_number': '+91 980000000' + empid[-1],
                    'is_staff': True,
                    'is_verified': True,
                    'account_status': 'ACTIVE',
                }
            )
            u.set_password('staff123')
            u.save()

            sp, _ = StaffProfile.objects.update_or_create(
                user=u,
                defaults={
                    'department': dept,
                    'designation': designation,
                    'employee_id': empid,
                    'max_active_capacity': 15,
                    'is_available': True,
                }
            )
            staff_objs[username] = u

        self.stdout.write(self.style.SUCCESS("[OK] Field Officers & Staff Profiles seeded."))

        # 6. Categories & Subcategories
        cats_data = [
            ('Roads', dept_objs['ROADS'], 'Potholes, broken pavements, road repairs', 'bi-cone-striped', 'HIGH',
             ['Potholes', 'Road Damage', 'Traffic Signal Malfunction', 'Road Maintenance & Resurfacing']),
            ('Water Supply', dept_objs['WATER'], 'Drinking water pipe leaks, contamination, low pressure', 'bi-droplet-half', 'HIGH',
             ['Pipeline Leakage', 'Low Water Pressure', 'Contaminated / Muddy Water', 'Water Meter Fault']),
            ('Electricity', dept_objs['ELEC'], 'Power cuts, sparks, transformer issues, dangling wires', 'bi-lightning-charge', 'CRITICAL',
             ['Power Outage', 'Transformer Sparking', 'Voltage Fluctuation', 'Loose / Dangling Cable']),
            ('Sanitation & Garbage', dept_objs['SANI'], 'Garbage clearing, street trash, dustbins', 'bi-trash', 'MEDIUM',
             ['Uncollected Garbage Dump', 'Overflowing Public Bin', 'Dead Animal Removal', 'Missing Dustbins']),
            ('Street Lights', dept_objs['LITE'], 'Broken bulbs, unlit dark streets, timers', 'bi-lightbulb', 'MEDIUM',
             ['Street Light Not Working', 'Flickering Lamp', 'Broken Pole / Fixture', 'Timer Misaligned']),
            ('Drainage & Sewage', dept_objs['HLTH'], 'Blocked storm drains, open manholes, sewer backflow', 'bi-water', 'HIGH',
             ['Blocked Stormwater Drain', 'Missing Manhole Cover', 'Open Gutter Hazard', 'Sewage Overflow']),
            ('Public Transport', dept_objs['TRAN'], 'Bus delays, shelter damage, route safety', 'bi-bus-front', 'LOW',
             ['Bus Delay & Schedule Breach', 'Damaged Bus Shelter', 'Driver / Conductor Misconduct', 'Route Frequency Issue']),
            ('Government Services', dept_objs['GEN'], 'Municipal counters, certificate processing', 'bi-building-gear', 'LOW',
             ['Delay in Processing Application', 'Counter Inactive During Hours', 'Public Facility Maintenance']),
        ]

        cat_objs = {}
        subcat_objs = {}
        for cat_name, dept, desc, icon, prio, sublist in cats_data:
            c, _ = Category.objects.update_or_create(
                name=cat_name,
                defaults={
                    'department': dept,
                    'description': desc,
                    'icon': icon,
                    'default_priority': prio,
                    'is_active': True,
                }
            )
            cat_objs[cat_name] = c
            for sname in sublist:
                s, _ = SubCategory.objects.update_or_create(
                    category=c,
                    name=sname,
                    defaults={'is_active': True}
                )
                subcat_objs[f"{cat_name}::{sname}"] = s

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(cat_objs)} Categories & subcategories populated."))

        # 7. Sample Realistic Complaints in Different Lifecycle Stages
        now = timezone.now()

        # Ticket 1: RESOLVED with Resolution Proof & 5-Star Feedback
        comp1, _ = Complaint.objects.update_or_create(
            complaint_id='RN-2026-000001',
            defaults={
                'user': john,
                'title': 'Severe Main Pipeline Burst Flooding 4th Cross Road',
                'description': 'A high-pressure drinking water main line burst this morning at 7:30 AM near house #42. Water is gushing onto the roadway, submerging footpaths and causing severe traffic disruption.',
                'category': cat_objs['Water Supply'],
                'subcategory': subcat_objs['Water Supply::Pipeline Leakage'],
                'priority': 'HIGH',
                'status': 'RESOLVED',
                'department': dept_objs['WATER'],
                'assigned_staff': staff_objs['officer_water'],
                'location_address': '4th Cross, Malleshwaram West, Metro Zone 4',
                'latitude': Decimal('12.9715987'),
                'longitude': Decimal('77.5945627'),
                'due_date': now + timedelta(days=2),
                'created_at': now - timedelta(days=2),
                'closed_at': now - timedelta(hours=4),
            }
        )
        ComplaintHistory.objects.get_or_create(
            complaint=comp1,
            new_status='SUBMITTED',
            defaults={'previous_status': None, 'changed_by': john, 'remarks': 'Submitted online with photo.'}
        )
        ComplaintHistory.objects.get_or_create(
            complaint=comp1,
            new_status='ASSIGNED',
            defaults={'previous_status': 'SUBMITTED', 'changed_by': admin_user, 'remarks': 'Assigned to Officer Robert Taylor.'}
        )
        ComplaintHistory.objects.get_or_create(
            complaint=comp1,
            new_status='RESOLVED',
            defaults={'previous_status': 'IN_PROGRESS', 'changed_by': staff_objs['officer_water'], 'remarks': 'Pipeline welded and valve sealed.'}
        )
        Resolution.objects.update_or_create(
            complaint=comp1,
            defaults={
                'resolved_by': staff_objs['officer_water'],
                'description': 'Repaired the cracked 8-inch cast iron pipe section using an engineered sleeve clamp. Replaced damaged pressure gasket. Roadway cleared and water flow restored with normal line pressure.',
                'remarks': 'Line flushed and pressure tested at 4.2 bar. Recommended secondary asphalt patch next week.',
                'verification_status': 'APPROVED',
                'verified_by': admin_user,
                'verified_at': now - timedelta(hours=3),
            }
        )
        ComplaintFeedback.objects.update_or_create(
            complaint=comp1,
            defaults={
                'user': john,
                'rating': 5,
                'satisfaction_level': 'VERY_SATISFIED',
                'resolution_quality': 'EXCELLENT',
                'comments': 'Outstanding and quick response by Officer Robert! The repair crew arrived within 3 hours and resolved the flooding completely.'
            }
        )
        ComplaintMessage.objects.get_or_create(
            complaint=comp1,
            sender=staff_objs['officer_water'],
            message='Emergency valve crew has been dispatched to shut off isolation valves.',
            defaults={'is_internal': False}
        )

        # Ticket 2: IN_PROGRESS (Roads)
        comp2, _ = Complaint.objects.update_or_create(
            complaint_id='RN-2026-000002',
            defaults={
                'user': sarah,
                'title': 'Deep Pothole Cluster Threatening Two-Wheelers near Metro Pillar 124',
                'description': 'A dangerous 1.5-foot crater has opened up in the center lane after recent rainfall. Several two-wheelers have skidded. Immediate cold mix patching required.',
                'category': cat_objs['Roads'],
                'subcategory': subcat_objs['Roads::Potholes'],
                'priority': 'HIGH',
                'status': 'IN_PROGRESS',
                'department': dept_objs['ROADS'],
                'assigned_staff': staff_objs['officer_roads'],
                'location_address': 'Outer Ring Road, Opp. Metro Pillar 124',
                'latitude': Decimal('12.9279232'),
                'longitude': Decimal('77.6271089'),
                'due_date': now + timedelta(days=1),
                'created_at': now - timedelta(days=1),
            }
        )
        ComplaintHistory.objects.get_or_create(
            complaint=comp2,
            new_status='SUBMITTED',
            defaults={'changed_by': sarah, 'remarks': 'Reported via web portal.'}
        )
        ComplaintHistory.objects.get_or_create(
            complaint=comp2,
            new_status='IN_PROGRESS',
            defaults={'previous_status': 'ASSIGNED', 'changed_by': staff_objs['officer_roads'], 'remarks': 'Road repair truck scheduled for night shift.'}
        )
        ComplaintMessage.objects.get_or_create(
            complaint=comp2,
            sender=staff_objs['officer_roads'],
            message='Safety cones placed around the crater. Asphalt cold-mix truck scheduled for 10 PM tonight.',
            defaults={'is_internal': False}
        )

        # Ticket 3: CRITICAL & ESCALATED (Electricity)
        comp3, _ = Complaint.objects.update_or_create(
            complaint_id='RN-2026-000003',
            defaults={
                'user': john,
                'title': 'High Voltage Transformer Sparking & Dangling Live Wire Near School Gate',
                'description': 'Distribution transformer #T-44 sparking intermittently with loud popping noises. One secondary phase conductor has snapped and is suspended 5 feet above the public sidewalk where schoolchildren walk.',
                'category': cat_objs['Electricity'],
                'subcategory': subcat_objs['Electricity::Loose / Dangling Cable'],
                'priority': 'CRITICAL',
                'status': 'UNDER_REVIEW',
                'department': dept_objs['ELEC'],
                'assigned_staff': staff_objs['officer_elec'],
                'location_address': 'Opposite St. Jude Primary School, Park View Road',
                'latitude': Decimal('12.9830271'),
                'longitude': Decimal('77.5806431'),
                'due_date': now - timedelta(hours=2),  # Intentionally overdue to test SLA
                'is_escalated': True,
                'escalation_level': 2,
                'escalation_reason': 'Breached 24-hour Critical SLA deadline.',
                'created_at': now - timedelta(hours=26),
            }
        )
        EscalationLog.objects.get_or_create(
            complaint=comp3,
            level=2,
            defaults={
                'reason': 'Automated SLA Breach: Critical hazard resolution passed 24h deadline.',
                'is_automated': True
            }
        )

        # Ticket 4: SUBMITTED (Sanitation)
        comp4, _ = Complaint.objects.update_or_create(
            complaint_id='RN-2026-000004',
            defaults={
                'user': sarah,
                'title': 'Commercial Waste Dump Left Unattended on Market Road',
                'description': 'Market vendors dumped large quantities of vegetable and packaging waste across the sidewalk. Stench is spreading into residential apartments.',
                'category': cat_objs['Sanitation & Garbage'],
                'subcategory': subcat_objs['Sanitation & Garbage::Uncollected Garbage Dump'],
                'priority': 'MEDIUM',
                'status': 'SUBMITTED',
                'department': dept_objs['SANI'],
                'assigned_staff': staff_objs['officer_sani'],
                'location_address': 'Vegetable Market Complex, 7th Sector',
                'latitude': Decimal('12.9512345'),
                'longitude': Decimal('77.5623412'),
                'due_date': now + timedelta(days=3),
                'created_at': now - timedelta(hours=3),
            }
        )

        # Ticket 5: REOPENED (Street Light)
        comp5, _ = Complaint.objects.update_or_create(
            complaint_id='RN-2026-000005',
            defaults={
                'user': john,
                'title': 'Continuous Streetlight Failure at 12th Main Dark Corner',
                'description': 'Three consecutive sodium vapor lamps remain dark at night, making the junction accident-prone and unsafe for pedestrians.',
                'category': cat_objs['Street Lights'],
                'subcategory': subcat_objs['Street Lights::Street Light Not Working'],
                'priority': 'MEDIUM',
                'status': 'REOPENED',
                'department': dept_objs['LITE'],
                'assigned_staff': None,
                'location_address': '12th Main & 8th Cross Corner, Phase 1',
                'latitude': Decimal('12.9644122'),
                'longitude': Decimal('77.6012431'),
                'due_date': now + timedelta(days=2),
                'is_escalated': True,
                'escalation_level': 2,
                'created_at': now - timedelta(days=4),
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] 5 Realistic Sample Complaints in multiple stages initialized."))
        self.stdout.write(self.style.SUCCESS("--- ResolveNow Seed Completed Successfully! ---"))
