# Feature Document — Labor Requirement Calculation Engine

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-5 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

This is the core output of the planning engine: converting aggregated task minutes into a required headcount per zone, role, shift, date, and time slot. This is the single most business-critical calculation in the product.

## 2. Scope

### In scope

- Aggregation of `TASK.quantity × TASK_TYPE.std_time_mins` grouped by zone + role + shift + slot.
- Headcount formula: `required_headcount = CEIL(total_task_minutes ÷ available_shift_minutes)`.
- Support for `source_type` of `forecast`, `actual`, or `blended` on `LABOR_REQUIREMENT`, including the transition behavior where actual orders arrive and replace/supersede forecast-driven tasks.
- Enforcement of Labor Plan Data Product contracts relevant to this entity (ERD reference §5.4): `required_headcount >= 1` always; requirement must reach `confirmed` ≥12h before shift start.
- Null/zero headcount observability check (ERD reference §7).

### Out of scope

- Matching requirements to actual employee shifts (separate feature: Labor Plan Matching).
- Forecast model quality itself (owned by Demand Signal Ingestion / external forecasting systems).

## 3. User Stories / Requirements

- As a warehouse manager, I want to see required headcount by zone and role for each upcoming shift, so I know how many people I need.
- As a labor planning PM, I want forecast-driven requirements to update automatically as real orders replace forecasts, so I get a continuously improving view of staffing needs.
- As the system, I want to alert the Labor Planning PM if any upcoming requirement has null/zero headcount, so a calculation failure doesn't go unnoticed.

## 4. Data Model Impact

Entity: `LABOR_REQUIREMENT` (ERD reference §2.14). Reads from `TASK`, `TASK_TYPE`, `SHIFT_TEMPLATE`. No new entities/fields proposed. No ERD version bump required.

## 5. API / Interface Design

- Internal aggregation job (batch or event-driven) writing `LABOR_REQUIREMENT` rows.
- `GET /labor-requirements?zone_id=&shift_template_id=&req_date=` — primary manager-facing read endpoint.
- `POST /labor-requirements/{id}/confirm` — transitions `status` `draft` → `confirmed`; `PUT` to `locked` once shift starts.
- Designed for agentic/API consumption per [CLAUDE.md](../../CLAUDE.md) §2 (agentic-first) — structured, filterable output, not UI-only.

## 6. Acceptance Criteria

- Given 600 units across 3 order lines at 0.5 mins/unit and a 480-minute shift, when the requirement is computed, then `required_headcount = 1` (matches ERD reference §4.2 walkthrough).
- Given a requirement with `required_headcount` null or zero for an upcoming shift, when the observability check runs, then the Labor Planning PM is alerted within 15 minutes.
- Given actual orders arrive replacing a forecast-driven task set, when recomputed, then `source_type` updates appropriately (e.g., `forecast` → `blended`/`actual`) and headcount reflects the new total.
- Given a requirement is not `confirmed` within 12 hours of shift start, when checked, then it is flagged per the Unconfirmed Plan observability check (ERD reference §7).

## 7. Test Cases

See [testcases/05-labor-requirement-calculation.md](../testcases/05-labor-requirement-calculation.md).

## 8. Open Questions

- Exact rule for how a forecast-driven task is "replaced" by an actual-order-driven task for the same demand (avoid double-counting).

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
