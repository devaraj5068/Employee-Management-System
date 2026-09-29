# Online Complaint Resolution Platform – ResolveNow

[![Python Version](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-092e20.svg)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1.svg)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ResolveNow** is a complete, production-grade, full-stack **Online Complaint Resolution Platform** built for civic bodies, municipalities, and enterprise complaint management. It enables citizens to register grievances online with geo-location pin-drops and multimedia attachments, track real-time resolution progress via a visual timeline, communicate directly with assigned field officers, and rate resolution quality. Administrators and departmental supervisors gain complete command-center oversight, automated SLA escalation, smart workload-balanced ticket routing, and comprehensive PDF/Excel analytics.

---

## 🌟 Key Highlights & Features

### 👤 Citizen / Public User Features
- **User Authentication**: Secure registration, email/phone OTP verification, login history tracking, and profile management.
- **Interactive Complaint Submission**:
  - Title, description, category, and dynamic AJAX subcategory selection.
  - Interactive **Leaflet + OpenStreetMap** pin-drop with HTML5 **"Use My Current Location"** and automatic reverse-geocoding.
  - Multi-file evidence uploads (Photos, Inspection PDFs, Word docs, Videos up to 15MB).
  - Auto-generated consecutive Complaint Reference IDs: `RN-YYYY-XXXXXX` (e.g. `RN-2026-000001`).
- **Official Acknowledgment Receipt**: On-screen printable receipt and instant downloadable **ReportLab PDF Receipt**.
- **Public & Authenticated Ticket Tracking**:
  - Public lookup by Complaint ID without requiring login.
  - Interactive **6-Step Visual Timeline**: `Submitted` &rarr; `Under Review` &rarr; `Assigned` &rarr; `In Progress` &rarr; `Resolved` &rarr; `Closed`.
  - SLA countdown deadline and overdue badge.
- **Direct Citizen-Officer Messaging**: Real-time communication thread for each complaint.
- **Citizen Feedback & Reopening**:
  - 5-Star rating, satisfaction level, and resolution quality reviews after resolution.
  - Ticket reopening workflow if work is incomplete, automatically re-escalating the ticket.

### 👷 Field Officer / Staff Features
- **Role-Based Staff Dashboard**: Live view of assigned tickets, urgent hazards, and active capacity utilization bar.
- **Workload Capacity Engine**: Tracks active ticket counts against max capacity limits (`max_active_capacity`).
- **Status & Progress Updates**: Advance complaint status with mandatory operational remarks and automated audit logs.
- **Resolution Submission Workflow**: Detailed repair summary, operational recommendations, and photo/document completion proofs.
- **Internal Staff Discussion Notes**: Post private technical notes hidden from citizens, visible only to fellow officers and admins.

### 👑 Administrator Command Center
- **Executive Analytics Dashboard**:
  - Live metric counters: Total, Today's, Pending, In Progress, Resolved, Closed, Reopened, Critical, SLA Overdue.
  - 5 Interactive **Chart.js** Visualizations:
    1. *Status Distribution* (Donut)
    2. *Priority Breakdown* (Pie)
    3. *Monthly Trend* (Line)
    4. *Top Categories* (Bar)
    5. *Department Workload* (Bar)
- **Automated Workload-Balanced Auto-Assignment**: Intelligent algorithm routes new complaints to the available officer with the lowest active workload in that department.
- **SLA & Automated Escalation Engine**:
  - Pre-configured SLA thresholds: Critical (24h), High (48h), Medium (96h), Low (168h).
  - Multi-tier escalation hierarchy: `Level 1 (Field Staff)` &rarr; `Level 2 (Dept Head)` &rarr; `Level 3 (Administrator)` &rarr; `Level 4 (Municipal Authority)`.
  - CLI / Cron / Celery automated overdue scanner (`python manage.py check_escalations`).
- **Geospatial City Map (`/location/map/`)**: Interactive Leaflet city map with colored pins, priority badges, and quick link popups.
- **Department & Category Administration**: Full CRUD for departments, categories, and subcategories.
- **Audit Trails & Security Compliance**: Immutable logging of all actions, logins, status changes, and client IP addresses.
- **Export & Reporting Engine**: Export executive reports to **PDF (`ReportLab`)**, **Excel (`openpyxl`)**, and **CSV**.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Backend Framework** | Python 3.10+ / 3.13, Django 4.2+ (LTS) |
| **Primary Database** | **MySQL 8.0+** (via `mysqlclient`) |
| **Frontend Framework** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Geospatial Mapping** | Leaflet.js, OpenStreetMap Tiles, Nominatim Reverse Geocoding API |
| **Data Analytics & Charts** | Chart.js 4.4+ |
| **Document & Report Generation** | ReportLab 4.x (PDF Receipts & Reports), openpyxl 3.1+ (Excel .xlsx), CSV |
| **REST API** | Django REST Framework (DRF) 3.14+ |
| **Background Tasks** | Celery 5.3+, Redis / Synchronous Management Command Fallback |
| **Email Service** | Django SMTP Email with Safe Local Console Fallback |

---

## 📂 Project Architecture

```text
digital_complaint_management/
│
├── config/                  # Project root settings, URLs, WSGI, ASGI, Celery
│   ├── settings.py          # MySQL configuration, installed apps, auth model
│   ├── urls.py              # Master URL routing and static/media handlers
│   ├── views.py             # Landing page, public metrics, error handlers
│   └── celery.py            # Celery broker and periodic task scheduler
│
├── accounts/                # CustomUser (CITIZEN, STAFF, ADMIN), OTP, RBAC, LoginHistory
├── departments/             # Municipal Departments (Roads, Water, Electricity, Sanitation, etc.)
├── staff/                   # Staff Profiles, Workload tracking, Auto-assignment engine
├── complaints/              # Complaint Lifecycle, Categories, Subcategories, Attachments, History
├── resolutions/             # Resolution submission, Proof photo upload, QA Verification, Reopening
├── communication/           # Complaint messaging threads, Citizen replies, Internal staff notes
├── notifications/           # In-app notification center, unread counters, SMTP email dispatcher
├── dashboard/               # Citizen, Field Officer, and Executive Admin Dashboards
├── reports/                 # Analytics views, ReportLab PDF export, openpyxl Excel export, CSV
├── feedback/                # 5-Star ratings, satisfaction levels, quality reviews, analytics
├── escalation/              # SLA rules, Overdue scanner service, Escalation logs, CLI command
├── location/                # Leaflet geospatial map view, marker clustering API
├── audit/                   # Activity audit logs, System configuration editor
├── api/                     # Django REST Framework ViewSets and serializers
│
├── templates/               # Reusable Bootstrap 5 templates (base, landing, dashboards, etc.)
├── static/                  # Custom CSS stylesheets, JS scripts, icons
├── media/                   # Uploaded citizen evidence and officer resolution photos
│
├── manage.py                # Django CLI management entry point
├── requirements.txt         # Pinned Python package dependencies
├── .env                     # Environment variables (MySQL credentials, secrets)
└── README.md                # Comprehensive documentation
```

---

## 🔑 Pre-Configured Demo Accounts

For instant academic project demonstration and evaluation, the following pre-configured accounts are seeded:

| Role | Username | Password | Email | Access Scope |
|---|---|---|---|---|
| **Administrator** | `admin` | `admin123` | `admin@resolvenow.org` | Full Command Center, System Settings, Audit Logs, Assignments |
| **Field Officer (Water)** | `officer_water` | `staff123` | `water.officer@resolvenow.org` | Water Dept Queue, Resolution Submission, Workload View |
| **Field Officer (Roads)** | `officer_roads` | `staff123` | `roads.officer@resolvenow.org` | Roads Dept Queue, Resolution Submission, Workload View |
| **Field Officer (Power)** | `officer_elec` | `staff123` | `elec.officer@resolvenow.org` | Electricity Dept Queue, Resolution Submission |
| **Citizen (Complainant 1)** | `citizen_john` | `citizen123` | `john.citizen@gmail.com` | File Complaints, Live Tracking, Messaging, Feedback |
| **Citizen (Complainant 2)** | `citizen_sarah` | `citizen123` | `sarah.smith@gmail.com` | File Complaints, Live Tracking, Messaging, Feedback |

> **Tip**: On the login page (`/accounts/login/`), click any of the **"Demo Quick Login Buttons"** to auto-fill credentials instantly!

---

## ⚙️ Installation & Quickstart

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed
- MySQL Server 8.0+ running locally on port `3306`
- Git (optional)

### Step 1: Open Terminal in Project Directory
```bash
cd "d:\edge\Employee Management System\digital_complaint_management"
```

### Step 2: (Optional) Create and Activate Virtual Environment
```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: MySQL Database Setup
Open MySQL command line or MySQL Workbench and create the database:
```sql
CREATE DATABASE IF NOT EXISTS digital_complaint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `.env` with your local MySQL password:
```env
DB_NAME=digital_complaint_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 5: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Seed Database with Realistic Demo Data
Populate departments, categories, subcategories, demo users, SLA rules, and realistic complaints:
```bash
python manage.py seed_data
```

### Step 7: Start the Development Server
```bash
python manage.py runserver
# Server starts automatically on port 8800:
# or explicitly: python manage.py runserver 8800
```

Open your browser and navigate to:
```text
http://127.0.0.1:8800/
```

---

## 🔄 Automated SLA Overdue Scanner

To scan the database for tickets that have exceeded their SLA resolution deadline and automatically escalate them through the hierarchy:
```bash
python manage.py check_escalations
```

In production, schedule this command via **Windows Task Scheduler**, Linux **Cron**, or **Celery Beat**:
```bash
# Example Celery Worker:
celery -A config worker --loglevel=info

# Example Celery Beat:
celery -A config beat --loglevel=info
```

---

## 🌐 Django REST Framework (DRF) API

ResolveNow provides complete RESTful endpoints for mobile application integration:

| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/auth/login/` | `POST` | User authentication & role retrieval | Public |
| `/api/auth/user/` | `GET` | Current authenticated user profile | Token / Session |
| `/api/complaints/` | `GET`, `POST` | List complaints or register new grievance | Authenticated |
| `/api/complaints/<id>/` | `GET`, `PUT` | Retrieve or update complaint details | Authenticated |
| `/api/categories/` | `GET` | List active categories & subcategories | Public |
| `/api/departments/` | `GET` | List civic departments | Public |
| `/api/staff/` | `GET` | List available field officers | Staff / Admin |
| `/api/notifications/` | `GET`, `PUT` | Notification feed & mark-read | Authenticated |
| `/api/feedback/` | `GET`, `POST` | View or submit citizen feedback | Authenticated |
| `/api/reports/summary/` | `GET` | High-level analytics metrics | Admin Only |

---

## 🧪 Running Automated Tests

ResolveNow includes an automated test suite verifying authentication, OTP verification, ID generation, status transitions, role permissions, PDF receipts, and Excel exports:

```bash
python manage.py test
```

Expected result:
```text
Found 16 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
................
----------------------------------------------------------------------
Ran 16 tests in 23.778s

OK
Destroying test database for alias 'default'...
```

---

## 🛡️ Security & Integrity Practices
1. **Password Encryption**: Django PBKDF2 with SHA-256 password hashing. Passwords are never stored in plain text.
2. **Strict RBAC**: `@citizen_required`, `@staff_required`, and `@admin_required` decorators ensure citizen privacy and prevent unauthorized access to tickets or admin modules.
3. **CSRF & XSS Prevention**: Built-in CSRF token verification on all POST operations and safe template auto-escaping.
4. **File Upload Security**: Upload file type validation (whitelist: JPG, PNG, WEBP, PDF, DOC, MP4) and 15MB file size limits.
5. **Audit Trail**: Every status change, assignment update, login attempt, and escalation writes an immutable record into `ActivityLog` with timestamp and client IP.

---

## 🎓 Academic Demonstration Guide

For final-year Computer Science & Engineering (CSE) project presentations:
1. **Public Persona**: Open `http://127.0.0.1:8800/` &rarr; Demonstrate landing page, live counters, and fast ticket search using `RN-2026-000001`.
2. **Citizen Persona**: Sign in as `citizen_john` &rarr; Submit a new complaint with map pin-drop &rarr; View acknowledgment receipt &rarr; Download official PDF receipt.
3. **Staff Persona**: Sign in as `officer_water` &rarr; View assigned tasks &rarr; Submit resolution work with description and photo proof &rarr; Ticket advances to Resolved.
4. **Citizen Rating**: Sign in as `citizen_john` &rarr; Submit 5-star rating and satisfaction review.
5. **Admin Command Center**: Sign in as `admin` &rarr; View 5 Chart.js analytics graphs &rarr; View staff workload analysis &rarr; Run SLA scan &rarr; Export PDF and Excel reports &rarr; Explore city geospatial map.

---

## 📄 License
This project is developed for academic presentation and enterprise civic tech implementation under the MIT License.
