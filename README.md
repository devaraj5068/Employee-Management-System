# Employee Management System (EMS)

A production-quality **Employee Management System** built using modern **Java 17**, **Spring Boot 3.2**, **Spring Security**, **Spring Data JPA (Hibernate)**, **MySQL 8 / H2 Database**, **Thymeleaf**, and **Bootstrap 5**.

---

## Key Features

- **Authentication & Authorization**:
  - Secure login/logout with BCrypt password encryption
  - Role-based authorization (`ROLE_ADMIN`, `ROLE_HR`, `ROLE_EMPLOYEE`)
  - Session management & Remember-Me functionality
  - Account activation/deactivation toggles for Administrators
  - Password change & forgot password workflows

- **Core Business Modules**:
  - **Employee Management**: Full CRUD, code auto-generation, filtering, sorting, pagination, and profile picture avatar support.
  - **Department Management**: Add, update, delete departments and view associated staff.
  - **Role & Security Management**: Role assignment and security rules.
  - **Attendance Module**: Live employee Check-In/Check-Out, work hour calculation, daily status marking, and monthly history.
  - **Salary & Payroll**: Net salary auto-calculation (`Net = Basic + Allowances - Deductions - Tax`), salary history, and printable PDF/HTML payslips.
  - **Reports & Exporting**: Export Employee, Attendance, and Salary data to Excel (`.xlsx`) and PDF (`.pdf`).
  - **Dashboard & Analytics**: Role-specific dashboards featuring KPI widgets and Chart.js graphs for workforce distribution and daily attendance breakdown.

---

## Technology Stack

- **Backend**: Java 17, Spring Boot 3.2.3, Spring Security 6, Spring Data JPA, Hibernate, Maven
- **Frontend**: HTML5, CSS3 (Custom Blue/White modern theme), JavaScript, Thymeleaf, Bootstrap 5.3.2, Bootstrap Icons
- **Database**: H2 (In-memory default for zero-setup execution), MySQL 8 (Production ready)
- **Reporting**: Apache POI (Excel generation), OpenPDF (PDF generation), Chart.js (Interactive UI graphs)

---

## Quick Start (Zero-Setup Execution)

1. Clone or import the project into **IntelliJ IDEA**, **Eclipse**, or **VS Code**.
2. Open terminal in project root and execute:
   ```bash
   mvn spring-boot:run
   ```
3. Open your browser and navigate to: `http://localhost:8888`

### Pre-Configured Demo Accounts:

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full Administrative & System Access |
| **HR Manager** | `hrmanager` | `hr123` | Employee, Attendance, Salary, Reports |
| **Employee** | `employee` | `emp123` | Personal Dashboard, Check-In/Out, Payslips |

---

## Documentation Links

- [Installation Guide](INSTALLATION.md)
- [API Documentation](API_DOCUMENTATION.md)
- [ER Diagram](ER_DIAGRAM.md)
- [UML Diagrams](UML_DIAGRAMS.md)
