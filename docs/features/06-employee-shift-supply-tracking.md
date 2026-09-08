# Feature Document — Employee Shift & Supply Tracking

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-6 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Labor requirements represent demand; this feature represents supply — which employees are actually scheduled and available. Without it, there is nothing for `LABOR_REQUIREMENT` to be matched against.

## 2. Scope

### In scope

- CRUD for `EMPLOYEE_SHIFT`: scheduling employees against `SHIFT_TEMPLATE` instances by date.
- Status lifecycle: `scheduled` → `confirmed` → `completed` / `absent`.
- Post-shift attendance capture: `actual_start`/`actual_end`, populated within 30 minutes of shift completion.
- Post-shift variance observability check (ERD reference §7): flag if `actual_start`/`actual_end` still null 30+ minutes after `end_time`.

### Out of scope

- Full time-and-attendance/payroll integration — this feature captures enough for variance analysis, not a payroll-grade attendance system.
- Publishing rosters to employees (rostering tool territory).

## 3. User Stories / Requirements

- As a warehouse manager, I want to schedule employees onto shift template instances, so there's a known supply pool to match against requirements.
- As a labor planning PM, I want actual start/end times captured promptly after each shift, so we can measure planned-vs-actual variance.
- As the system, I want to alert the warehouse manager if attendance isn't recorded within 30 minutes of shift end, so gaps in data don't silently accumulate.

## 4. Data Model Impact

Entity: `EMPLOYEE_SHIFT` (ERD reference §2.15). No new entities/fields proposed. No ERD version bump required.

## 5. API / Interface Design

- `POST/GET/PUT /employee-shifts` — scheduling and status updates
- `POST /employee-shifts/{id}/attendance` — records `actual_start`/`actual_end`
- `GET /employee-shifts?employee_id=&shift_date=&status=`

## 6. Acceptance Criteria

- Given an employee scheduled to a shift template for a date, when queried, then the record appears as available supply for that zone-eligible role via `EMPLOYEE_ROLE`.
- Given a shift's `end_time` has passed by more than 30 minutes with no `actual_end`, when the check runs, then the warehouse manager is alerted.
- Given attendance is recorded, when saved, then `actual_start`/`actual_end` are stored and available for variance reporting.

## 7. Test Cases

See [testcases/06-employee-shift-supply-tracking.md](../testcases/06-employee-shift-supply-tracking.md).

## 8. Open Questions

- Source of attendance capture — manual manager entry, badge/clock integration, or both?

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
