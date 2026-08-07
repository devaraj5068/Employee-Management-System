# UML Class & Sequence Diagrams

This document illustrates the Object-Oriented Architecture and key runtime interactions of the Employee Management System.

---

## 1. Class Diagram

```mermaid
classDiagram
    class User {
        +Long id
        +String username
        +String email
        +String password
        +boolean enabled
        +Set~Role~ roles
    }

    class Role {
        +Long id
        +String name
        +String description
    }

    class Employee {
        +Long id
        +String employeeCode
        +String firstName
        +String lastName
        +String email
        +String mobileNumber
        +LocalDate joiningDate
        +EmploymentStatus employmentStatus
        +getFullName() String
    }

    class Department {
        +Long id
        +String code
        +String name
        +String location
    }

    class Attendance {
        +Long id
        +LocalDate attendanceDate
        +LocalTime checkInTime
        +LocalTime checkOutTime
        +Double workHours
        +AttendanceStatus status
    }

    class Salary {
        +Long id
        +String payMonth
        +BigDecimal basicSalary
        +BigDecimal hra
        +BigDecimal netSalary
        +calculateNetSalary() void
    }

    User "1" <--> "1" Employee
    Department "1" o-- "*" Employee
    Role "1" o-- "*" Employee
    User "*" <--> "*" Role
    Employee "1" o-- "*" Attendance
    Employee "1" o-- "*" Salary
```

---

## 2. Sequence Diagram - Employee Check-In Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Employee
    participant UI as Browser / Thymeleaf UI
    participant Ctrl as AttendanceController
    participant Service as AttendanceService
    participant Repo as AttendanceRepository

    Employee->>UI: Click "Check In"
    UI->>Ctrl: POST /attendance/checkin
    Ctrl->>Service: checkIn(employeeId)
    Service->>Repo: findByEmployeeIdAndAttendanceDate(empId, today)
    alt Record exists & checked in
        Repo-->>Service: Return Attendance Record
        Service-->>Ctrl: Throw ValidationException ("Already checked in")
        Ctrl-->>UI: Redirect with error message
    else First punch of day
        Service->>Repo: save(Attendance[PRESENT, checkInTime=Now])
        Repo-->>Service: Saved Attendance Entity
        Service-->>Ctrl: AttendanceDTO
        Ctrl-->>UI: Redirect to Dashboard with success toast
    end
```
