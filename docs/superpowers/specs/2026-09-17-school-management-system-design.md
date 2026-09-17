# School Management System — Production Architecture Design

**Date:** 2026-09-17  
**Target:** Aman Ahmadzai Private School  
**Application:** Native Windows desktop application, offline-first  
**Stack:** Python 3.12+, PySide6, SQLAlchemy, SQLite, ReportLab, openpyxl, bcrypt, PyInstaller

## 1. Goal

Evolve the existing desktop School Management System into a production-level school administration and academic management application while preserving the existing working database, authentication, reporting, backup, and dashboard behavior.

The system must enforce authorization at both UI and business/data layers. Hiding a button is not considered sufficient security.

## 2. Existing Baseline

The current application already has SQLAlchemy models for User, Student, Teacher, Fee, Payment, Activity, and Setting; bcrypt password hashing; SQLite; configurable application directories; PDF reporting; and a PySide6 desktop UI. The application stores mutable data below `%LOCALAPPDATA%\\SchoolManagementSystem`.

The first implementation phase must extend this baseline rather than replace it blindly. Existing records must remain migratable and existing login/database behavior must continue to work.

## 3. Architecture

```text
PySide6 Presentation
        |
        v
Application / Service Layer
        |
        +--> Authentication
        +--> Authorization / RBAC
        +--> Data-level Restrictions
        +--> Audit Logging
        +--> Reporting
        +--> Backup / Restore
        |
        v
SQLAlchemy Data Access Layer
        |
        v
SQLite Database
```

Presentation code must not be the only place where authorization is enforced. Services that mutate protected records must call authorization checks before performing the operation.

## 4. Identity, Roles and Permissions

### Roles

- Super Admin
- School Admin
- Principal
- Vice Principal
- Academic Manager
- Teacher
- Accountant
- Receptionist
- Librarian
- HR Officer
- Exam Officer
- Attendance Officer
- Parent
- Student
- Security/Guard
- Transport Manager
- Store Manager

### Permission actions

- view
- create
- edit
- delete
- print
- export
- import
- approve
- reject
- pay
- collect
- manage
- restore
- backup

Permissions are stored as records rather than hard-coded role checks. A role receives many permissions through a RolePermission relationship. Users may have one or more roles through UserRole.

Recommended permission key format:

`module.action`

Examples:

- `students.view`
- `students.create`
- `students.edit`
- `students.delete`
- `students.promote`
- `students.transfer`
- `students.withdraw`
- `students.print_id`
- `students.export`
- `results.enter_marks`
- `results.edit_marks`
- `results.approve`
- `finance.collect`
- `finance.refund`
- `users.manage`
- `system.backup`
- `system.restore`
- `audit.view`

## 5. Authorization Flow

```text
Logged-in User
     |
     v
Assigned Role(s)
     |
     v
Permission Check
     |
     v
Data Restriction Check
     |
     v
Business Rule Check
     |
     v
Perform Action
     |
     v
Audit Log
```

Examples:

Teacher may access attendance and marks only for assigned classes/subjects. Accountant may access fees, payments, expenses and financial reports but not marks. Exam Officer may enter and edit marks according to the configured permission policy. Only authorized administrators can manage users, system settings, backup and restore.

## 6. Data-Level Security

Authorization must support ownership/assignment scopes in addition to module permissions.

Scope types:

- own records
- assigned classes
- assigned subjects
- assigned students
- own department
- whole school

A Teacher's query must be filtered by their assigned classes/subjects before records are returned. The same restriction must be applied to edit/delete/attendance/marks operations.

## 7. Core Database Design

### Security

- users
- roles
- permissions
- user_roles
- role_permissions
- login_attempts
- user_sessions (or equivalent session/audit state)
- audit_logs

### School configuration

- settings
- school_profile
- academic_years
- academic_calendar
- grade_rules

### Students and parents

- students
- student_guardians
- parents
- student_documents
- student_health_records
- student_discipline_records
- student_transport_assignments

### Staff

- teachers
- employees
- departments
- job_positions
- employee_documents
- employee_attendance
- employee_leaves
- payroll
- payroll_items
- employee_performance

### Academics

- classes
- sections
- subjects
- class_subjects
- teacher_subject_assignments
- class_teacher_assignments
- student_enrollments
- student_promotions
- student_transfers
- student_withdrawals

### Attendance

- student_attendance
- teacher_attendance
- attendance_statuses

### Exams and results

- exams
- exam_schedules
- exam_subjects
- marks
- grade_rules
- results
- result_items
- certificates

### Finance

- fee_structures
- student_fees
- payments
- payment_allocations
- refunds
- scholarships
- discounts
- expenses
- expense_categories

### Library

- books
- book_categories
- authors
- publishers
- book_copies
- library_issues
- library_returns
- library_fines

### Transport

- vehicles
- drivers
- routes
- route_stops
- transport_assignments
- vehicle_maintenance
- fuel_records

### Inventory

- inventory_items
- inventory_categories
- suppliers
- purchases
- purchase_items
- stock_movements

### Communication

- announcements
- notifications
- messages

### Documents and branding

- document metadata where required
- school logo stored in the configured application image directory
- report/print configuration in settings

## 8. Student Lifecycle

```text
Admission
  -> Enrollment
  -> Attendance / Fees / Exams / Library / Transport / Health / Discipline
  -> Promotion / Transfer
  -> Withdrawal / Graduation
```

Student records must use stable internal IDs and human-readable codes such as `STU-000001` and must not rely on names as foreign-key identifiers.

## 9. Teacher and Employee Lifecycle

```text
Recruitment/Profile
  -> Department / Position
  -> Class & Subject Assignment
  -> Attendance / Leave / Payroll / Performance
  -> Documents / ID Card
```

## 10. Academic Structure

Academic year contains classes. Classes contain sections. Subjects are assigned to classes. Teachers are assigned to subjects/classes. Students are enrolled into a class-section for an academic year.

This structure replaces dependence on free-text `class_name` and `section` fields over time. Existing fields should be migrated rather than abruptly removed.

## 11. Exams and Results

Required controls:

- exam types
- exam schedules
- subject marks
- passing marks
- grade rules
- total and percentage calculation
- GPA where configured
- pass/fail
- position/ranking rules configurable by school policy
- result approval
- report cards
- transcripts
- certificates

Marks editing and deletion must be permission-protected and audited. Approved results should require explicit permission to reopen/edit.

## 12. Attendance

Student and employee/teacher attendance support:

- present
- absent
- late
- leave
- excused

Reports:

- daily
- weekly
- monthly
- yearly
- student-wise
- class-wise
- teacher-wise

## 13. Finance

Support fee structures, admission/monthly/exam/transport/library/other fees, discounts, scholarships, payments, receipts, dues, refunds, expenses and financial reports.

Money operations must use explicit transaction records and must never silently overwrite historical payments. Refunds and corrections must create auditable records.

## 14. Audit Logging

Every sensitive create/edit/delete/approve/reject/payment/refund/backup/restore/login/security action must record:

- user
- action
- module
- record type/id
- timestamp
- computer/session identifier where available
- old value snapshot where appropriate
- new value snapshot where appropriate
- result/status

Audit logs are append-oriented. Normal users must not delete or edit them.

## 15. Authentication and Security

- password hashes only; never plain text
- bcrypt or Argon2
- failed-login tracking
- configurable account lockout
- password change
- optional password expiry
- logout
- inactive-session timeout
- role verification
- permission verification
- default-password warning/change flow

The existing default development administrator must not remain an unsafe production credential after installation; first-run setup should require an administrator to change the default password.

## 16. Backup and Restore

Backup types:

- manual database backup
- scheduled daily/weekly backup
- full application backup where appropriate

Restore flow:

```text
Select Backup
  -> Validate Backup
  -> Administrator Confirmation
  -> Create Safety Backup
  -> Restore
  -> Verify Database
  -> Audit Log
```

The system must not restore over the active database without creating a pre-restore safety copy.

## 17. UI/UX

Main layout:

```text
+-------------------------------------------------------------+
| School Logo | School Name        Search  Bell  User  Menu |
+-------------------+-----------------------------------------+
| Dashboard         |                                         |
| Students          |                                         |
| Teachers          |              Main Content               |
| Academics         |                                         |
| Attendance        |                                         |
| Exams             |                                         |
| Results           |                                         |
| Fees & Finance    |                                         |
| HR                |                                         |
| Library           |                                         |
| Transport         |                                         |
| Inventory         |                                         |
| Health            |                                         |
| Discipline        |                                         |
| Communication     |                                         |
| Reports           |                                         |
| Settings          |                                         |
+-------------------+-----------------------------------------+
```

Features:

- professional dashboard cards
- sidebar navigation
- top navigation
- searchable/filterable tables
- pagination for large lists
- dialogs with validation
- confirmation dialogs for destructive operations
- success/error notifications
- loading indicators
- keyboard shortcuts
- light/dark theme
- Pashto RTL default
- English LTR
- school logo/branding

Navigation and actions must be generated/filtered according to permissions.

## 18. Branding

School profile must support:

- school name in Pashto and English
- logo upload/update/preview
- address
- phone
- email
- website
- principal name
- academic year
- motto
- registration number

Branding is reused in login, dashboard, student/teacher ID cards, receipts, result cards, certificates, reports and letterhead.

## 19. Reporting

All applicable modules should expose print/export operations according to permissions.

Formats:

- print preview
- PDF
- Excel
- CSV

Reports must include school branding and generation metadata where appropriate.

## 20. Localization

Use the existing translation infrastructure rather than hard-coding UI text. Pashto is the default language and should use RTL layout; English uses LTR. Dates, numbers, labels, menus, dialogs and report headings should follow the selected language.

## 21. Migration Strategy

Do not drop the existing tables in the first phase. Introduce new normalized tables alongside the current schema, add migration/backfill logic, then update application services to use the normalized structures.

Existing `User.role` should be migrated into Role/UserRole. Existing `Activity` should be migrated or mapped into AuditLog while retaining compatibility until the new audit system is active. Existing Student class/section text should be mapped into Class/Section/Enrollment.

## 22. Implementation Phases

### Phase 1 — Foundation

- schema migration framework/strategy
- roles
- permissions
- user-role relationships
- authorization service
- audit logs
- login attempt/security controls
- tests

### Phase 2 — Academic Core

- academic years
- classes/sections/subjects
- student enrollment
- teacher assignments
- student/teacher restrictions

### Phase 3 — Students and Teachers

- complete profiles
- guardians
- documents
- promotion/transfer/withdrawal
- teacher/employee records

### Phase 4 — Attendance, Exams, Results

- attendance
- exam scheduling
- marks
- grade rules
- result approval
- report cards/certificates

### Phase 5 — Finance and HR

- fee structures
- payments/receipts
- refunds
- expenses
- payroll
- leave

### Phase 6 — Library, Transport, Inventory, Health, Discipline

Implement each module with its own permissions, validation, audit trail and reports.

### Phase 7 — Communication, Reports and Branding

- announcements
- notifications
- messages
- branded reports
- ID cards
- certificates

### Phase 8 — Settings, Backup, Hardening and Packaging

- settings
- backup/restore
- security hardening
- migration validation
- full regression tests
- PyInstaller build
- Windows installer verification

## 23. Testing Strategy

Tests must cover authorization before implementation is considered complete:

- permission allow/deny matrix
- role assignment
- data-scope restrictions
- teacher class/subject isolation
- accountant finance isolation
- protected marks editing
- protected user/settings/backup operations
- audit log creation
- login lockout
- password hashing
- backup/restore safety
- migration compatibility
- critical CRUD/service behavior

UI tests should verify that unauthorized navigation/actions are hidden or disabled, but service-layer tests must remain the authoritative security checks.

## 24. Definition of Done

A module is complete only when:

1. Database model and relationships exist.
2. Service/business rules exist.
3. Permission checks exist at the service layer.
4. Data-level restrictions are enforced where applicable.
5. UI respects permissions.
6. Sensitive operations create audit records.
7. Validation and error handling exist.
8. Required reports/exports exist.
9. Tests cover critical behavior.
10. Existing functionality remains compatible unless intentionally migrated.
