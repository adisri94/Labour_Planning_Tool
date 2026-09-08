# Feature Document — Labor Plan Matching (Demand ↔ Supply)

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-7 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

This is the final planning output: matching computed `LABOR_REQUIREMENT` records to actual `EMPLOYEE_SHIFT` supply, producing the plan warehouse managers act on. This is the primary consumer-facing output of the entire system.

## 2. Scope

### In scope

- Matching engine: search `EMPLOYEE_SHIFT` for employees qualified (via `EMPLOYEE_ROLE`) and scheduled during the relevant shift, and create `LABOR_PLAN` records allocating headcount to a `LABOR_REQUIREMENT`.
- Support for partial allocation: multiple `LABOR_PLAN` records can fulfill one requirement; one employee shift can contribute to multiple requirements.
- Enforcement: sum of `planned_headcount` across plans for a requirement must equal `required_headcount`.
- Plan lifecycle: `draft` → `confirmed` → `executed`, with `confirmed` required before shift start.
- Unconfirmed Plan observability check (ERD reference §7): alert warehouse manager + Labor Planning PM if a plan is still `draft` within 14 hours of scheduled shift start.

### Out of scope

- Cross-warehouse employee borrowing/transfer logic (assume single-warehouse matching for this iteration; flag as backlog candidate if needed).
- Automatic overtime/regulation-violating assignment — the matcher must respect `LABOR_REGULATION` constraints, not override them.

## 3. User Stories / Requirements

- As a warehouse manager, I want the system to propose which employee shifts fulfill each requirement, so I don't have to manually cross-reference qualifications and availability.
- As a labor planning PM, I want a requirement's plan allocations to always sum to its required headcount, so there's no silent under- or over-staffing in the data.
- As the system, I want to flag any plan still in `draft` within 14 hours of shift start, so managers have time to act before it's too late.

## 4. Data Model Impact

Entity: `LABOR_PLAN` (ERD reference §2.16). Reads from `LABOR_REQUIREMENT`, `EMPLOYEE_SHIFT`, `EMPLOYEE_ROLE`, `LABOR_REGULATION`. No new entities/fields proposed. No ERD version bump required.

## 5. API / Interface Design

- `POST /labor-requirements/{id}/plan` — triggers matching engine, returns proposed `LABOR_PLAN` record(s)
- `PUT /labor-plans/{id}` — adjust `planned_headcount`, transition `plan_status`
- `GET /labor-plans?labor_requirement_id=` and `?employee_shift_id=`
- `created_at` timestamp preserved on every record for audit/version history (already in ERD).

## 6. Acceptance Criteria

- Given a requirement needing 1 picker and one qualified, scheduled employee shift, when matching runs, then a `LABOR_PLAN` record is created with `planned_headcount = 1`.
- Given partial allocation across two employee shifts, when both are confirmed, then their `planned_headcount` sum equals the requirement's `required_headcount`.
- Given a plan still `draft` 14 hours before shift start, when the check runs, then both the warehouse manager and Labor Planning PM are alerted.
- Given a regulation constraint (e.g., max hours/day) would be violated by a proposed allocation, when matching runs, then that allocation is not proposed.

## 7. Test Cases

See [testcases/07-labor-plan-matching.md](../testcases/07-labor-plan-matching.md).

## 8. Open Questions

- Tie-breaking rule when multiple qualified employee shifts are available (e.g., primary role holders first, per `EMPLOYEE_ROLE.is_primary`)?
- Should the matcher auto-confirm plans under some confidence threshold, or always require manager confirmation?

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
