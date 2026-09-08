# Feature Document — Task Engine (Task Type & Task Generation)

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-4 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

This is the bridge layer that converts raw demand (orders, forecasts) into atomic, measurable units of work with an engineered standard time — the direct input to the headcount formula. Without it, demand volume can't be translated into labor minutes.

## 2. Scope

### In scope

- CRUD and governance for `TASK_TYPE` (including the governed `std_time_mins` field).
- Task generation logic: create `TASK` records from `ORDER_LINE` (`source_type = actual`) and from `DEMAND_FORECAST` (`source_type = forecast`).
- Support for one order line generating multiple tasks across zones/types (per ERD reference §2.11, §2.13).
- `std_time_mins` governance: IE + Labor Planning PM approval required; `change_log` audit table (`task_type_id`, `old_value`, `new_value`, `changed_by`, `changed_at`, `approved_by`); DB constraint `std_time_mins > 0`.

### Out of scope

- The Labor Requirement aggregation itself (separate feature — this feature stops at producing `TASK` records).
- Automatic re-forecast/re-training of standard times (IE sets these manually based on time studies).

## 3. User Stories / Requirements

- As an IE, I want to define a task type with a standard time per zone, so task volume can be converted to labor minutes.
- As a warehouse system, I want a task auto-generated whenever an order line is created, so actual demand flows into planning without manual entry.
- As a labor planning PM, I want any change to `std_time_mins` to require dual approval and be logged, so a single bad edit can't silently distort headcount across the facility.

## 4. Data Model Impact

Entities: `TASK_TYPE`, `TASK` (ERD reference §2.12–2.13). New supporting table: `task_type_change_log` (not in ERD v2 — proposed addition). **This requires an ERD version bump (v2 → v3)** per the schema change protocol (ERD reference §6.2) before implementation.

## 5. API / Interface Design

- `POST/GET/PUT /task-types` (write requires `approved_by` + triggers `change_log` entry on `std_time_mins` change)
- `GET /task-types/{id}/change-log`
- Internal event-driven task generation: `order_line.created` → generate `TASK`(s); `demand_forecast.created` → generate `TASK`(s)
- `GET /tasks?zone_id=&scheduled_date=&status=`

## 6. Acceptance Criteria

- Given a `std_time_mins` change without both IE and PM approval recorded, when saved, then the write is rejected.
- Given an approved `std_time_mins` change, when saved, then a `change_log` row is written and re-computation of the next 14 days of `LABOR_REQUIREMENT` for the affected zone is triggered.
- Given a new `ORDER_LINE` with quantity 600 and pick_type requiring Unit Pick, when processed, then one or more `TASK` records are created with `source_type = actual` summing to the correct quantity.
- Given `std_time_mins <= 0`, when saved, then the write is rejected (DB constraint).

## 7. Test Cases

See [testcases/04-task-engine.md](../testcases/04-task-engine.md).

## 8. Open Questions

- Exact rule for splitting one order line into multiple tasks across zones (e.g., pick + pack) — is this driven by a zone routing table not yet in the ERD?

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
