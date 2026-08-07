# API Documentation

This document describes key Web & REST endpoints provided by the Employee Management System.

---

## Authentication & Public Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/login` | Render Login Page | Public |
| POST | `/login` | Process Form Authentication | Public |
| GET | `/register` | Render Registration Form | Public |
| POST | `/register` | Process New User & Employee Registration | Public |
| GET | `/forgot-password` | Render Password Reset Page | Public |
| POST | `/logout` | Logout current session | Authenticated |

---

## Employee Management Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/employees` | List, search, filter, and paginate employees | ADMIN, HR |
| GET | `/employees/add` | Form to create a new employee | ADMIN, HR |
| POST | `/employees/add` | Process creation of new employee record | ADMIN, HR |
| GET | `/employees/view/{id}` | View detailed employee profile | ADMIN, HR |
| GET | `/employees/edit/{id}` | Form to edit employee profile | ADMIN, HR |
| POST | `/employees/edit/{id}` | Update existing employee record | ADMIN, HR |
| POST | `/employees/delete/{id}` | Delete employee record | ADMIN |

---

## Department & Role Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/departments` | List all departments | ADMIN, HR |
| POST | `/departments/add` | Create department | ADMIN, HR |
| POST | `/departments/edit/{id}` | Update department | ADMIN, HR |
| POST | `/departments/delete/{id}` | Delete department | ADMIN |
| GET | `/roles` | List security roles | ADMIN |
| POST | `/roles/add` | Add security role | ADMIN |
| POST | `/roles/delete/{id}` | Delete security role | ADMIN |

---

## Attendance Module Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/attendance/checkin` | Employee daily self Check-In | EMPLOYEE, HR, ADMIN |
| POST | `/attendance/checkout` | Employee daily self Check-Out | EMPLOYEE, HR, ADMIN |
| GET | `/attendance/my` | View personal attendance log | EMPLOYEE |
| GET | `/attendance/all` | View company-wide attendance directory | ADMIN, HR |
| POST | `/attendance/mark` | Manually mark or edit attendance | ADMIN, HR |

---

## Salary & Payroll Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/salary/all` | List & filter company salary slips | ADMIN, HR |
| GET | `/salary/my` | View employee personal payslips | EMPLOYEE |
| GET | `/salary/create` | Form to generate new salary slip | ADMIN, HR |
| POST | `/salary/create` | Save new salary slip | ADMIN, HR |
| GET | `/salary/slip/{id}` | View printable monthly salary slip | Authenticated Owner, HR, ADMIN |

---

## Export & Report Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/reports` | Render Report Generator Dashboard | ADMIN, HR |
| GET | `/reports/export/excel` | Download generated Excel report (`.xlsx`) | ADMIN, HR |
| GET | `/reports/export/pdf` | Download generated PDF report (`.pdf`) | ADMIN, HR |
