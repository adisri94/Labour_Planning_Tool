# Test Cases — Facility & Org Master Data

- **Feature Doc**: [link](../features/01-facility-org-master-data.md)
- **Status**: Approved

## Test Cases — US-1: View zones and capacity within a warehouse

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-1 | Happy path | List zones for a warehouse with zones | Warehouse `wh-001` exists with 3 zones seeded | `GET /warehouses/wh-001/zones` | 200; response is a list of 3 zones, each with `name`, `zone_type`, `capacity` |
| TC-2 | Edge case | List zones for a warehouse with none | Warehouse `wh-002` exists with 0 zones | `GET /warehouses/wh-002/zones` | 200; response is `[]`, not an error |
| TC-3 | Edge case | Zone isolation across warehouses | Warehouses `wh-001` and `wh-002` each have their own zones | `GET /warehouses/wh-001/zones` | Response contains only zones with `warehouse_id = wh-001`; no `wh-002` zones present |
| TC-4 | Failure mode | Invalid `zone_type` rejected | Warehouse `wh-001` exists | `POST /warehouses/wh-001/zones` with `zone_type: "loading_dock"` (not in allowed enum) | 422; error identifies `zone_type` as the invalid field |
| TC-5 | UI / happy path | Frontend renders seeded zones | Seed data loaded via `db/init_db.py` | Open warehouse page for `wh-001` in the frontend | Zone names and capacities are visibly rendered without a manual API call |

## Test Cases — US-2: Register an employee and certify job roles

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-6 | Happy path | Create an employee | Warehouse `wh-001` exists | `POST /employees` with valid payload (warehouse_id, name, employee_type, employment_status, hire_date) | 201; response includes generated `id` and echoes submitted fields |
| TC-7 | Failure mode | Active employee with zero roles rejected | New employee payload has `employment_status: "active"`, no roles attached yet | `POST /employees` then attempt to persist as active with no `EMPLOYEE_ROLE` | 422; error identifies missing-role contract (ERD reference §5.1) |
| TC-8 | Happy path | Attach a role satisfies the contract | Employee created per TC-6/TC-7 flow, `job_role_id` for "Picker" exists | `POST /employees/{id}/roles` with `{job_role_id, certified_date, is_primary: true}` | 201; `EMPLOYEE_ROLE` record created; employee now satisfies ≥1-role contract; subsequent `GET /employees/{id}` no longer errors on the active-with-no-role rule |
| TC-9 | Edge case | Multiple `is_primary = true` roles | Employee already has one role with `is_primary: true` | `POST /employees/{id}/roles` with a second role, also `is_primary: true` | Both records persist (no uniqueness constraint enforced yet) — flagged as Open Question in the Feature Doc; test documents current (permissive) behavior, to be revisited if a decision is made |
| TC-10 | Failure mode | Invalid `employee_type` rejected | Warehouse `wh-001` exists | `POST /employees` with `employee_type: "seasonal"` (not in allowed enum) | 422; error identifies `employee_type` as invalid |
| TC-11 | Failure mode | Invalid `employment_status` rejected | Warehouse `wh-001` exists | `POST /employees` with `employment_status: "furloughed"` (not in allowed enum) | 422; error identifies `employment_status` as invalid |

## Test Cases — US-3: Employment status changes are immediately correct

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-12 | Happy path | Terminate an employee | Employee exists with `employment_status: "active"` | `PUT /employees/{id}` with `employment_status: "terminated"` | 200; update persisted |
| TC-13 | Happy path | Immediate read-after-write consistency | Employee just updated per TC-12 | `GET /employees/{id}` immediately after TC-12 | Response shows `employment_status: "terminated"` with no delay |
| TC-14 | Happy path | Filter excludes terminated employees | At least one `active` and one `terminated` employee exist in `wh-001` | `GET /employees?warehouse_id=wh-001&employment_status=active` | Response excludes the terminated employee from TC-12 |

## Test Cases — US-4: Demo-ready seed data on first run

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-15 | Happy path | Fresh DB bootstrap | No `labor_planning.db` file exists | Run `python db/init_db.py` | Script exits 0; `labor_planning.db` file is created |
| TC-16 | Happy path | Seed data completeness | TC-15 completed | `GET /warehouses`, `GET /warehouses/{id}/zones`, `GET /job-roles`, `GET /employees` | ≥1 warehouse, 3–4 zones, 3–4 job roles, ~10–15 employees returned, each employee with ≥1 `EMPLOYEE_ROLE` |
| TC-17 | Edge case | Re-running init against an existing DB | `labor_planning.db` already exists and is seeded (TC-15 already run) | Run `python db/init_db.py` again | Script either errors clearly (no silent duplication) or deterministically resets/re-seeds — documented behavior in the script; test asserts row counts are unchanged or reset to the same known seed count, never duplicated |

## Test Cases — Feature-wide data quality (ERD reference §5.1)

| ID | Type | Scenario | Preconditions | Steps | Expected Result |
|----|------|----------|----------------|-------|------------------|
| TC-18 | Failure mode | `labor_rate <= 0` rejected | — | `POST /job-roles` with `labor_rate: 0` | 422; write rejected |
| TC-19 | Failure mode | Negative `labor_rate` rejected | — | `POST /job-roles` with `labor_rate: -5.0` | 422; write rejected |
| TC-20 | Failure mode | Missing required non-null field | — | `POST /employees` omitting `name` | 422; error identifies `name` as required |

## Coverage Notes

- TC-1 through TC-5 cover US-1's acceptance criteria in [01-facility-org-master-data.md](../features/01-facility-org-master-data.md) Section 3.
- TC-6 through TC-11 cover US-2.
- TC-12 through TC-14 cover US-3, including the explicit scope boundary that this feature only guarantees immediate correctness within its own store, not the 30-minute downstream propagation SLA (owned by later features).
- TC-15 through TC-17 cover US-4 and directly validate the [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) `db/init_db.py` bootstrap flow.
- TC-18 through TC-20 cover the Workforce Master Data Product quality contracts (ERD reference §5.1) not already exercised by a specific user story.
- TC-9 is intentionally a documentation test, not a hard pass/fail gate — revisit once the `is_primary` open question is resolved.
