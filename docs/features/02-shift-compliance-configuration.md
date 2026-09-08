# Feature Document — Shift & Compliance Configuration

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-2 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Labor requirements are always expressed within a shift window, and shifts are subject to legal/contractual constraints. Without configurable shift templates and regulations, the planning engine cannot compute `available_shift_minutes` or guarantee compliant plans.

## 2. Scope

### In scope

- CRUD for `SHIFT_TEMPLATE`, `LABOR_REGULATION`, and the `REGULATION_SHIFT` bridge.
- Enforcement of Shift & Compliance Data Product quality contracts (ERD reference §5.2): `start_time`/`end_time` non-null; `max_hours_per_day`/`max_hours_per_week` > 0.
- Legal sign-off workflow gate before a regulation or shift template change activates.
- Computation helper: available working minutes per shift template (accounting for `break_interval_mins`), used by the Labor Requirement Calculation feature.

### Out of scope

- Automated legal interpretation of new regulations — legal sign-off is a human step, not something this feature automates.

## 3. User Stories / Requirements

- As an operations admin, I want to define a shift template (start/end time, days of week, type), so requirements can be computed against a real time window.
- As a compliance officer, I want to attach one or more regulations to a shift template, so the plan respects max hours and break rules.
- As a labor planning PM, I want changes to regulations blocked until legal sign-off is recorded, so we never operate out of compliance.

## 4. Data Model Impact

Entities: `SHIFT_TEMPLATE`, `LABOR_REGULATION`, `REGULATION_SHIFT` (ERD reference §2.6–2.8). No new entities/fields proposed. No ERD version bump required.

## 5. API / Interface Design

- `POST/GET/PUT /warehouses/{id}/shift-templates`
- `POST/GET /labor-regulations`
- `POST /shift-templates/{id}/regulations` (manage `REGULATION_SHIFT`)
- `GET /shift-templates/{id}/available-minutes` — derived helper endpoint

## 6. Acceptance Criteria

- Given a shift template with no `end_time`, when saved, then the write is rejected.
- Given a regulation change with no recorded legal sign-off, when activation is attempted, then it is blocked.
- Given a 9-hour shift with a 60-minute break, when available minutes are requested, then the result is 480 (matches ERD reference §4.1 walkthrough).

## 7. Test Cases

See [testcases/02-shift-compliance-configuration.md](../testcases/02-shift-compliance-configuration.md).

## 8. Open Questions

- Where does "legal sign-off" get recorded — a field on `LABOR_REGULATION`, or tracked entirely in the Decision Log?

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
