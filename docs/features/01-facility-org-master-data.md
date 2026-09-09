# Feature Document — Facility & Org Master Data

- **Status**: Approved
- **Approved by**: Aditya Srivastava (2026-09-08)
- **Related sprint**: Sprint 1, Phase 1 (Must Have) — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md), [RELEASE_PLAN.md](../RELEASE_PLAN.md)
- **Related backlog item(s)**: BL-1 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Every other feature in this tool is scoped to a warehouse, zone, employee, or job role. Without a trustworthy master-data foundation, none of the downstream demand, task, or requirement calculations have anything reliable to hang off. This is Sprint 1 — the first feature built, and the first slice of the local mock data source described in [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md). It establishes the root entities and the Workforce Master data product (ERD reference §5.1).

## 2. Scope

### In scope

- CRUD and validation for `WAREHOUSE`, `ZONE`, `EMPLOYEE`, `JOB_ROLE`, `EMPLOYEE_ROLE`.
- The `db/schema.sql` DDL for these five tables, plus `db/seed_data.sql` rows for a demoable single warehouse.
- FastAPI routers + SQLAlchemy models for these entities, per [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) `/backend/app/models` and `/backend/app/api`.
- Enforcement of Workforce Master Data Product quality contracts (ERD reference §5.1): `EMPLOYEE.id/name/employee_type` non-null; every active employee has ≥1 `EMPLOYEE_ROLE`; `JOB_ROLE.labor_rate > 0`.
- Propagation behavior for `employment_status` changes (e.g., termination) — in this local-demo architecture there is no separate HR feed to "propagate from," so this means: an update to `employment_status` is immediately queryable, and downstream availability queries (a stub for now — no other feature exists yet to consume it) must treat `terminated` employees as excluded. The 30-minute SLA in the ERD reference is a contract downstream features must honor once they exist (see Feature 06/07); this feature's job is only to make the status change atomic and correctly stored.
- Minimal frontend views: a warehouse/zone list and an employee list with role assignment, per [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) `/frontend/src/pages`.

### Out of scope

- Payroll processing (HCM/payroll system of record remains external).
- Rostering/schedule publishing UI (separate system).
- HCM (Workday) feed integration — seed data is manually authored for the demo; see Open Questions.
- Any authentication/authorization (explicit non-goal of the local demo architecture — see [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) §8).

## 3. User Stories / Requirements

### US-1 — View zones and capacity within a warehouse

As a warehouse manager, I want to see which zones exist in my warehouse and their capacity, so I can plan within physical constraints.

**Acceptance Criteria**

- Given a warehouse with one or more zones, when I call `GET /warehouses/{id}/zones`, then I receive all zones for that warehouse with `name`, `zone_type`, and `capacity`.
- Given a warehouse with no zones yet, when I call `GET /warehouses/{id}/zones`, then I receive an empty list (not an error).
- Given a zone belonging to a different warehouse, when I call `GET /warehouses/{id}/zones` for a warehouse it does not belong to, then that zone is not included in the response.
- Given a `zone_type` value outside the allowed set (`receiving`, `putaway`, `picking`, `sorting`, `packing`, `shipping`), when creating a zone, then the write is rejected with a 422.
- Given the minimal frontend, when a user opens the warehouse page for a warehouse with seeded zones, then each zone's name and capacity are visibly rendered without a manual API call.

### US-2 — Register an employee and certify job roles

As an HR/workforce admin, I want to register an employee and certify them for one or more job roles, so the planning engine can consider them for those roles.

**Acceptance Criteria**

- Given valid employee data (`warehouse_id`, `name`, `employee_type`, `employment_status`, `hire_date`), when I call `POST /employees`, then a new `EMPLOYEE` record is created and returned with a generated `id`.
- Given a newly created employee with `employment_status = active` and no `EMPLOYEE_ROLE` attached, when the record is saved, then the API rejects it with a 422 identifying the missing-role contract (ERD reference §5.1).
- Given an existing employee, when I call `POST /employees/{id}/roles` with a valid `job_role_id`, `certified_date`, and `is_primary`, then the `EMPLOYEE_ROLE` bridge record is created and the employee now satisfies the ≥1-role contract.
- Given an employee already certified in one role with `is_primary = true`, when a second role is attached with `is_primary = true`, then both records are allowed to coexist unless a later feature defines a single-primary constraint — flagged as an open question (see Section 8) rather than silently enforced here.
- Given an `employee_type` or `employment_status` value outside the ERD's enumerated set, when creating or updating an employee, then the write is rejected with a 422.

### US-3 — Employment status changes are immediately correct

As a labor planning PM, I want employment status changes stored correctly and immediately queryable, so a terminated employee is never available to be planned into a shift by later features.

**Acceptance Criteria**

- Given an active employee, when I call `PUT /employees/{id}` with `employment_status = terminated`, then the update succeeds and is persisted.
- Given an employee just updated to `terminated`, when I immediately call `GET /employees/{id}` or `GET /employees?employment_status=active`, then the response reflects `terminated` / excludes that employee, respectively, with no observable delay within this feature's own data store.
- Given the 30-minute propagation SLA from ERD reference §5.1, when a downstream feature (06/07) later queries availability, then it is that feature's responsibility to treat `terminated` as unavailable — this feature only guarantees the status value itself is correct and immediately readable.

### US-4 — Demo-ready seed data on first run

As anyone replicating this repo for a demo, I want `db/init_db.py` to give me a warehouse with zones, employees, and job roles already populated, so I have something to show without manual data entry.

**Acceptance Criteria**

- Given a fresh clone of the repo with no existing `labor_planning.db`, when I run `python db/init_db.py`, then the script completes without error and creates the file.
- Given the script has completed, when I call `GET /warehouses`, `GET /warehouses/{id}/zones`, `GET /job-roles`, and `GET /employees`, then each returns the seeded records described in Section 4.2 (≥1 warehouse, 3–4 zones, 3–4 job roles, ~10–15 employees each with ≥1 role).
- Given `db/init_db.py` is run a second time against an existing `labor_planning.db`, when it completes, then it does not silently duplicate seed rows (either it errors clearly, or it resets/re-seeds deterministically — behavior to be decided during implementation and documented in the script itself).

## 4. Data Model Impact

Entities: `WAREHOUSE`, `ZONE`, `EMPLOYEE`, `JOB_ROLE`, `EMPLOYEE_ROLE` (ERD reference §2.1–2.5). No new entities/fields proposed — this feature implements the model as-is. No ERD version bump required.

### 4.1 DDL sketch (`db/schema.sql` — this feature's portion)

```sql
CREATE TABLE warehouse (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    timezone TEXT NOT NULL
);

CREATE TABLE zone (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    zone_type TEXT NOT NULL CHECK (zone_type IN ('receiving','putaway','picking','sorting','packing','shipping')),
    capacity INTEGER
);

CREATE TABLE job_role (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    skill_level TEXT CHECK (skill_level IN ('entry','intermediate','senior')),
    labor_rate REAL NOT NULL CHECK (labor_rate > 0)
);

CREATE TABLE employee (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    employee_type TEXT NOT NULL CHECK (employee_type IN ('full_time','part_time','temporary')),
    employment_status TEXT NOT NULL CHECK (employment_status IN ('active','on_leave','terminated')),
    hire_date TEXT
);

CREATE TABLE employee_role (
    employee_id TEXT NOT NULL REFERENCES employee(id),
    job_role_id TEXT NOT NULL REFERENCES job_role(id),
    certified_date TEXT,
    is_primary INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (employee_id, job_role_id)
);
```

Constraints match the ERD reference exactly (`labor_rate > 0`, enumerated status/type fields). The "≥1 `EMPLOYEE_ROLE` per active employee" contract is enforced at the application layer (service-level check on activation), not as a DB constraint, since SQLite cannot express a cross-table cardinality constraint declaratively.

### 4.2 Seed data (`db/seed_data.sql` — this feature's portion)

One warehouse ("Chicago FC-1", US-based per [DECISION_LOG.md](../DECISION_LOG.md) 2026-09-10), 3–4 zones (Picking, Packing, Receiving, Shipping), 3–4 job roles (Picker, Packer, Forklift Operator, Receiver) with USD hourly `labor_rate` values, and ~10–15 employees with role certifications — enough to make Feature 05's worked example (ERD reference §4) demonstrable once later sprints land.

## 5. API / Interface Design

Base path convention and error/pagination envelope follow the conventions to be formalized in Feature 10 (Sprint 8); this feature adopts a reasonable default now rather than waiting, per [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) §7.

| Method | Path | Description |
|---|---|---|
| `POST` | `/warehouses` | Create a warehouse |
| `GET` | `/warehouses` | List warehouses |
| `GET` | `/warehouses/{id}` | Get one warehouse |
| `PUT` | `/warehouses/{id}` | Update a warehouse |
| `POST` | `/warehouses/{id}/zones` | Create a zone under a warehouse |
| `GET` | `/warehouses/{id}/zones` | List zones for a warehouse |
| `PUT` | `/zones/{id}` | Update a zone |
| `POST` | `/job-roles` | Create a job role |
| `GET` | `/job-roles` | List job roles |
| `POST` | `/employees` | Create an employee |
| `GET` | `/employees?warehouse_id=&employment_status=` | List/filter employees |
| `PUT` | `/employees/{id}` | Update an employee (including `employment_status`) |
| `POST` | `/employees/{id}/roles` | Attach an `EMPLOYEE_ROLE` (job_role_id, certified_date, is_primary) |
| `GET` | `/employees/{id}/roles` | List an employee's certified roles |

Payloads are JSON with field names matching ERD attribute names, staying close to WFM/HCM (Workday-style) export shapes per [CLAUDE.md](../../CLAUDE.md) §1–2. Example:

```json
POST /employees
{
  "warehouse_id": "wh-001",
  "name": "Aditi Rao",
  "employee_type": "full_time",
  "employment_status": "active",
  "hire_date": "2025-01-15"
}
```

## 6. Acceptance Criteria

Acceptance criteria are defined per user story in Section 3 (US-1 through US-4). Two feature-wide criteria apply across all stories:

- Given a `JOB_ROLE` with `labor_rate <= 0`, when saved, then the write is rejected (DB constraint + API-level validation error) — supports US-2's role-certification flow.
- Given any request violating an ERD-defined enum or non-null constraint (Section 4.1), when submitted to any endpoint in Section 5, then the API returns a 422 with a field-level error, not a silent partial write.

## 7. Test Cases

See [testcases/01-facility-org-master-data.md](../testcases/01-facility-org-master-data.md).

## 8. Open Questions

- Source of truth for initial employee load in a *real* (non-demo) deployment — manual entry vs. HCM feed (Workday) integration timing. Not blocking for this sprint since seed data is manually authored, but worth flagging before Phase 2.
- Exact wording/format of the 422 validation error envelope — should be finalized consistently with whatever Feature 10 standardizes in Sprint 8; this feature will use a simple `{"error": "...", "field": "..."}` shape in the meantime and adjust if Feature 10 changes it.
- Whether `EMPLOYEE_ROLE.is_primary = true` should be constrained to at most one per employee (raised in US-2's acceptance criteria) — the ERD reference doesn't state this explicitly; needs a decision before Feature 07 (Labor Plan Matching) relies on "primary role" semantics.

## 9. Approval

- [x] Reviewed by product owner
- [x] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
