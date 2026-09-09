# Feature Document — Shift & Compliance Configuration

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: Sprint 2, Phase 1 (Must Have) — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md), [RELEASE_PLAN.md](../RELEASE_PLAN.md)
- **Related backlog item(s)**: BL-2 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Labor requirements are always expressed within a shift window, and shifts are subject to legal/contractual constraints. Without configurable shift templates and regulations, the planning engine cannot compute `available_shift_minutes` or guarantee compliant plans. This is Sprint 2 — the second slice of the local mock data source, extending `db/schema.sql`/`seed_data.sql` and the FastAPI backend established in Sprint 1.

## 2. Scope

### In scope

- CRUD for `SHIFT_TEMPLATE`, `LABOR_REGULATION`, and the `REGULATION_SHIFT` bridge.
- Enforcement of Shift & Compliance Data Product quality contracts (ERD reference §5.2): `start_time`/`end_time` non-null; `max_hours_per_day`/`max_hours_per_week` > 0.
- An activation gate standing in for the "legal sign-off" workflow (see Section 4.3 — resolves the Sprint-1-era open question): a shift template or regulation is created `is_active = false` by default and cannot be attached to/used by other features until explicitly activated via a dedicated endpoint, which records who activated it in-app and expects a corresponding [Decision Log](../DECISION_LOG.md) entry citing the actual legal sign-off.
- Computation helper: available working minutes per shift template (accounting for `break_interval_mins` sourced from its linked regulation(s)), used by Feature 05 (Labor Requirement Calculation).
- `db/schema.sql`/`seed_data.sql` extension for these three tables; minimal frontend view (shift templates + attached regulations, with an activate action).

### Out of scope

- Automated legal interpretation of new regulations — legal sign-off is a human step, not something this feature automates.
- Enforcing `max_hours_per_day`/`max_hours_per_week` against actual `EMPLOYEE_SHIFT` data — that enforcement belongs to Feature 07 (Labor Plan Matching), which reads these regulation values but doesn't yet exist. This feature only stores and validates the regulation configuration itself.

## 3. User Stories / Requirements

### US-1 — Define a shift template

As an operations admin, I want to define a shift template (start/end time, days of week, type), so requirements can be computed against a real time window.

**Acceptance Criteria**

- Given valid shift data (`warehouse_id`, `name`, `start_time`, `end_time`, `shift_type`, `days_of_week`), when I call `POST /warehouses/{id}/shift-templates`, then a new `SHIFT_TEMPLATE` is created with `is_active = false` by default.
- Given a shift template with no `end_time`, when saved, then the write is rejected with a 422.
- Given a `shift_type` outside the allowed set (`day`, `afternoon`, `night`), when saved, then the write is rejected with a 422.
- Given an inactive shift template, when queried via `GET /warehouses/{id}/shift-templates`, then it is still returned (visible for review) but flagged `is_active: false` — inactive does not mean hidden, it means not yet usable by other features.

### US-2 — Attach regulations to a shift template

As a compliance officer, I want to attach one or more regulations to a shift template, so the plan respects max hours and break rules.

**Acceptance Criteria**

- Given an existing `SHIFT_TEMPLATE` and an existing `LABOR_REGULATION`, when I call `POST /shift-templates/{id}/regulations` with `regulation_id`, then a `REGULATION_SHIFT` bridge record is created.
- Given a shift template with two attached regulations with different `break_interval_mins`, when available minutes are computed (US-3), then the calculation uses the most restrictive (longest) mandatory break among attached regulations — see Section 4.2 for the exact rule.
- Given a `LABOR_REGULATION` with `max_hours_per_day <= 0` or `max_hours_per_week <= 0`, when saved, then the write is rejected with a 422.
- Given an attempt to attach a regulation that is `is_active = false`, when `POST /shift-templates/{id}/regulations` is called, then the write is rejected with a 422 (an unactivated regulation cannot govern a shift yet).

### US-3 — Compute available shift minutes

As the Labor Requirement Calculation engine (Feature 05, not yet built), I need a reliable `available_shift_minutes` value per shift template, so headcount can be computed correctly once that feature lands.

**Acceptance Criteria**

- Given a 9-hour shift template (540 minutes gross) with an attached regulation specifying `break_interval_mins = 60`, when `GET /shift-templates/{id}/available-minutes` is called, then the result is 480 (matches ERD reference §4.1 walkthrough).
- Given a shift template with no attached regulations, when available minutes are requested, then the result equals the gross shift duration (no break deducted) — flagged as a reasonable default in Open Questions, not an ERD-stated rule.
- Given a shift template whose `end_time` is earlier than `start_time` (e.g., an overnight shift, 22:00–06:00), when available minutes are requested, then the calculation correctly wraps past midnight rather than returning a negative duration.

### US-4 — Block usage of unactivated (unsigned-off) configuration

As a labor planning PM, I want changes to shift templates/regulations blocked from being used until legal sign-off is recorded, so we never operate out of compliance.

**Acceptance Criteria**

- Given a newly created `SHIFT_TEMPLATE` or `LABOR_REGULATION` (`is_active = false`), when any other feature (e.g., Feature 05/06) attempts to reference it, then this feature's API rejects the linkage attempt at the point of attachment (see US-2's fourth criterion) rather than relying on the consuming feature to check.
- Given an admin calls `POST /shift-templates/{id}/activate` (or `/labor-regulations/{id}/activate`), when the call succeeds, then `is_active` flips to `true` and an `activated_by`/`activated_at` pair is recorded on the record.
- Given a record is activated, when I check the [Decision Log](../DECISION_LOG.md), then I expect (as a process step, not an automated check) a corresponding entry citing the real-world legal sign-off — this feature enforces the *gate*, not the *evidence*; the evidence lives in the Decision Log by process convention.

## 4. Data Model Impact

Entities: `SHIFT_TEMPLATE`, `LABOR_REGULATION`, `REGULATION_SHIFT` (ERD reference §2.6–2.8).

### 4.1 Resolving the Sprint-1-era open question: where legal sign-off is recorded

Decision: no new ERD entity. Add two fields not currently in the ERD reference to `SHIFT_TEMPLATE` and `LABOR_REGULATION`: `is_active` (boolean, default `false`) and `activated_by` / `activated_at`. **This is a schema addition and requires an ERD version bump (v2 → v3)** per the schema change protocol (ERD reference §6.2), to be applied alongside Feature 04's proposed `task_type_change_log` addition if both are approved close together — or independently if Feature 04 isn't approved yet by the time this ships. Since these are additive (new nullable/defaulted columns, not a breaking change), the ≥24h backward-compatibility rule is satisfied trivially in this single-repo/local-demo context; the ≥5-business-day consumer notice does not apply since there are no external consumers of this schema yet.

### 4.2 Available-minutes calculation rule

```
gross_minutes = (end_time - start_time), wrapping past midnight if end_time < start_time
break_minutes = MAX(break_interval_mins across all is_active regulations attached via REGULATION_SHIFT)
               = 0 if no active regulations attached
available_shift_minutes = gross_minutes - break_minutes
```

This mirrors the ERD reference §4.1 example exactly (540 − 60 = 480) and is the direct input Feature 05 will consume.

### 4.3 DDL sketch (`db/schema.sql` — this feature's additions)

```sql
CREATE TABLE IF NOT EXISTS shift_template (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    shift_type TEXT NOT NULL CHECK (shift_type IN ('day','afternoon','night')),
    days_of_week INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 0,
    activated_by TEXT,
    activated_at TEXT
);

CREATE TABLE IF NOT EXISTS labor_regulation (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    max_hours_per_day INTEGER NOT NULL CHECK (max_hours_per_day > 0),
    max_hours_per_week INTEGER NOT NULL CHECK (max_hours_per_week > 0),
    break_interval_mins INTEGER,
    overtime_multiplier REAL,
    region TEXT,
    is_active INTEGER NOT NULL DEFAULT 0,
    activated_by TEXT,
    activated_at TEXT
);

CREATE TABLE IF NOT EXISTS regulation_shift (
    regulation_id TEXT NOT NULL REFERENCES labor_regulation(id),
    shift_template_id TEXT NOT NULL REFERENCES shift_template(id),
    PRIMARY KEY (regulation_id, shift_template_id)
);

CREATE INDEX IF NOT EXISTS idx_shift_template_warehouse ON shift_template(warehouse_id);
```

### 4.4 Seed data (`db/seed_data.sql` — this feature's additions)

For warehouse `wh-001`: two shift templates ("Morning Shift" 06:00–15:00, "Night Shift" 22:00–06:00 next day — to exercise the midnight-wrap case), both `is_active = true` (pre-activated in seed data so Sprint 3+ demos aren't blocked); one `LABOR_REGULATION` ("Factories Act 1948"-style, `max_hours_per_day=9`, `max_hours_per_week=48`, `break_interval_mins=60`), also seeded `is_active = true`, attached to both shift templates via `REGULATION_SHIFT`.

## 5. API / Interface Design

| Method | Path | Description |
|---|---|---|
| `POST` | `/warehouses/{id}/shift-templates` | Create a shift template (`is_active = false` by default) |
| `GET` | `/warehouses/{id}/shift-templates` | List shift templates for a warehouse |
| `PUT` | `/shift-templates/{id}` | Update a shift template |
| `POST` | `/shift-templates/{id}/activate` | Activate (records `activated_by`, `activated_at`) |
| `GET` | `/shift-templates/{id}/available-minutes` | Computed available working minutes (Section 4.2) |
| `POST` | `/labor-regulations` | Create a regulation (`is_active = false` by default) |
| `GET` | `/labor-regulations` | List regulations |
| `POST` | `/labor-regulations/{id}/activate` | Activate a regulation |
| `POST` | `/shift-templates/{id}/regulations` | Attach an active regulation (`REGULATION_SHIFT`) |
| `GET` | `/shift-templates/{id}/regulations` | List regulations attached to a shift template |

Example:

```json
POST /warehouses/wh-001/shift-templates
{
  "id": "shift-morning",
  "name": "Morning Shift",
  "start_time": "06:00",
  "end_time": "15:00",
  "shift_type": "day",
  "days_of_week": 62
}
```

## 6. Acceptance Criteria

Acceptance criteria are defined per user story in Section 3 (US-1 through US-4).

## 7. Test Cases

See [testcases/02-shift-compliance-configuration.md](../testcases/02-shift-compliance-configuration.md).

## 8. Open Questions

- Default available-minutes behavior when no regulation is attached (assumed: no break deducted) — reasonable but not ERD-stated; revisit if a warehouse without any regulation turns out to need a default break assumption.
- Whether `activated_by` should validate against a real user/auth system — moot for now since this local demo has no authentication (per [SOLUTION_ARCHITECTURE.md](../SOLUTION_ARCHITECTURE.md) §8); `activated_by` is a free-text field for the demo.
- This feature proposes an ERD v3 bump (`is_active`/`activated_by`/`activated_at` on two entities) — confirm whether to apply this now or batch it with Feature 04's proposed change, and update [labor-planning-erd-reference-v2.md](../reference/labor-planning-erd-reference-v2.md)'s changelog (Section 9) accordingly once decided.

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
