# Feature Document — Observability & Data Health Monitoring

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-9 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Per the ERD reference §7, the system must be able to report its own health without manual investigation. This feature implements the automated checks and alerting that make each data product trustworthy in production, and underpins the "production grade" and "data-as-a-product" objectives from the Initiative Objectives.

## 2. Scope

### In scope

- Continuous automated checks, alerting within 15 minutes of breach, per ERD reference §7:
  - Forecast freshness check (no `DEMAND_FORECAST` newer than 2h for an active warehouse-zone pair) → Demand Planning team.
  - Null headcount check (`LABOR_REQUIREMENT.required_headcount` null/zero for an upcoming shift) → Labor Planning PM.
  - Unconfirmed plan check (`LABOR_PLAN` still `draft` within 14h of shift start) → Warehouse manager + Labor Planning PM.
  - `std_time_mins` drift check (changed without an approved `change_log` entry in preceding 24h) → IE + Labor Planning PM.
  - Post-shift variance check (`actual_start`/`actual_end` still null 30+ min after shift `end_time`) → Warehouse manager.
- A minimal dashboard/API surfacing current health status per check, per warehouse.

### Out of scope

- General application performance monitoring (APM) / infrastructure observability (logs, traces) — this feature is specifically the data-health checks defined in the ERD reference, not general ops tooling.

## 3. User Stories / Requirements

- As a Labor Planning PM, I want to be alerted automatically when a requirement has null/zero headcount, so I catch calculation failures before they affect a shift.
- As a warehouse manager, I want to know if a plan is still unconfirmed 14 hours before shift start, so I have time to react.
- As Industrial Engineering, I want to be alerted if `std_time_mins` changed without proper approval, so governance bypasses are caught quickly.

## 4. Data Model Impact

No new core entities. May require a lightweight `health_check_alert` log table (check name, entity, warehouse/zone, breached_at, alerted_at, resolved_at) to track alert history — proposed addition, **requires ERD version bump** if adopted.

## 5. API / Interface Design

- Scheduled jobs (e.g., every 5 minutes) executing each check.
- `GET /health-checks?warehouse_id=` — current status per check.
- Alert delivery mechanism TBD (see Open Questions) — must reach the owning team within 15 minutes of breach per the ERD reference's SLA.

## 6. Acceptance Criteria

- Given no `DEMAND_FORECAST` newer than 2 hours for an active zone, when the check runs, then Demand Planning is alerted within 15 minutes.
- Given a `LABOR_REQUIREMENT.required_headcount` is null for an upcoming shift, when the check runs, then the Labor Planning PM is alerted within 15 minutes.
- Given a `std_time_mins` value changed without a matching `change_log` entry in the last 24h, when the check runs, then both IE and the Labor Planning PM are alerted.

## 7. Test Cases

See [testcases/09-observability-data-health.md](../testcases/09-observability-data-health.md).

## 8. Open Questions

- Alert delivery channel (email/Slack/in-app) — depends on what's available in the deployment environment.
- Retention period for alert history.

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
