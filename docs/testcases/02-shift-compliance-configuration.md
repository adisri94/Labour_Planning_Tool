# Test Cases — Shift & Compliance Configuration

- **Feature Doc**: [link](../features/02-shift-compliance-configuration.md)
- **Status**: Approved

## Test Cases — US-1: Define a shift template

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-1 | Happy path | Create a shift template | Warehouse `wh-001` exists | `POST /warehouses/wh-001/shift-templates` with valid payload | 201; `is_active: false` in response |
| TC-2 | Failure mode | Missing `end_time` rejected | Warehouse `wh-001` exists | `POST /warehouses/wh-001/shift-templates` omitting `end_time` | 422 |
| TC-3 | Failure mode | Invalid `shift_type` rejected | Warehouse `wh-001` exists | `POST /warehouses/wh-001/shift-templates` with `shift_type: "swing"` | 422 |
| TC-4 | Edge case | Inactive template still visible | Shift template created per TC-1 (inactive) | `GET /warehouses/wh-001/shift-templates` | Response includes the template with `is_active: false` — not hidden |

## Test Cases — US-2: Attach regulations to a shift template

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-5 | Happy path | Attach an active regulation | Shift template and an active `LABOR_REGULATION` exist | `POST /shift-templates/{id}/regulations` with `regulation_id` | 201; `REGULATION_SHIFT` created |
| TC-6 | Failure mode | Attach an inactive regulation rejected | Shift template exists; regulation exists with `is_active: false` | `POST /shift-templates/{id}/regulations` with that `regulation_id` | 422; write rejected |
| TC-7 | Failure mode | `max_hours_per_day <= 0` rejected | — | `POST /labor-regulations` with `max_hours_per_day: 0` | 422 |
| TC-8 | Failure mode | `max_hours_per_week <= 0` rejected | — | `POST /labor-regulations` with `max_hours_per_week: -5` | 422 |
| TC-9 | Edge case | Most restrictive break wins | Shift template has two active regulations attached, `break_interval_mins` 30 and 60 respectively | `GET /shift-templates/{id}/available-minutes` | Calculation deducts 60 (the max), not 30 or their sum |

## Test Cases — US-3: Compute available shift minutes

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-10 | Happy path | ERD worked example matches | 9-hour shift template (06:00–15:00), one active regulation with `break_interval_mins: 60` attached | `GET /shift-templates/{id}/available-minutes` | Returns `480` |
| TC-11 | Edge case | No regulation attached | Shift template exists with zero attached regulations | `GET /shift-templates/{id}/available-minutes` | Returns the full gross duration (no break deducted) |
| TC-12 | Edge case | Overnight shift wraps past midnight | Shift template 22:00–06:00, one active regulation with `break_interval_mins: 30` | `GET /shift-templates/{id}/available-minutes` | Gross duration computed as 480 minutes (8 hours), not negative; available minutes = 450 |

## Test Cases — US-4: Block usage of unactivated configuration

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-13 | Happy path | Activate a shift template | Shift template exists with `is_active: false` | `POST /shift-templates/{id}/activate` with `{"activated_by": "PM Name"}` | 200; `is_active: true`, `activated_by`/`activated_at` populated |
| TC-14 | Happy path | Activate a regulation | Regulation exists with `is_active: false` | `POST /labor-regulations/{id}/activate` | 200; `is_active: true`, `activated_by`/`activated_at` populated |
| TC-15 | Failure mode | Re-attach after deactivation-equivalent check | Inactive regulation (never activated) | `POST /shift-templates/{id}/regulations` with that regulation's id | 422 (same as TC-6 — confirms the gate holds regardless of entry point) |
| TC-16 | Process check | Decision Log expectation | A shift template/regulation was just activated (TC-13/TC-14) | Manually review [DECISION_LOG.md](../DECISION_LOG.md) | A corresponding entry exists citing the real-world legal sign-off — this is a process/documentation check, not an automated assertion |

## Test Cases — Seed data (US-1–US-3 combined)

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-17 | Happy path | Seed data bootstraps active shift config | Fresh `db/init_db.py` run | `GET /warehouses/wh-001/shift-templates`, `GET /labor-regulations` | 2 shift templates and 1 regulation returned, all `is_active: true`, regulation attached to both templates |
| TC-18 | Happy path | Seeded morning shift available-minutes | TC-17 completed | `GET /shift-templates/shift-morning/available-minutes` | Returns `480` |

## Coverage Notes

- TC-1–TC-4 cover US-1; TC-5–TC-9 cover US-2; TC-10–TC-12 cover US-3; TC-13–TC-16 cover US-4.
- TC-17–TC-18 validate the seed data extension described in the Feature Doc Section 4.4, ensuring Sprint 3+ features have pre-activated shift/regulation data to build against.
- TC-16 is intentionally a manual/process check, not an automated test — flag if a future feature (e.g., Feature 08/09) should turn this into an automated drift check.
