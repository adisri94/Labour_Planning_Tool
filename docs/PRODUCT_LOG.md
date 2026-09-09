# Product Log — Warehouse Labor Planning Tool

This document records what was finalized and shipped at the end of each development sprint — the product-facing complement to [DECISION_LOG.md](DECISION_LOG.md) (which records *why* decisions were made). It is the audit trail referenced by [CLAUDE.md](../CLAUDE.md) Section 5 (Documentation Discipline).

Add one entry per sprint, at sprint close, once its scope is actually finalized — not mid-sprint. Keep entries append-only; if something shipped in a sprint is later reverted or reworked, note that in the sprint where the revert happens rather than editing history.

## How to add an entry

Copy the template below, fill it in, and append it under "Log" in reverse-chronological order (newest on top).

```
### Sprint <N> — [YYYY-MM-DD start] to [YYYY-MM-DD end]

- **Goal**: What this sprint set out to deliver.
- **Shipped**: Features, entities, APIs, or fixes finalized this sprint (bullet list).
- **Data model impact**: Any ERD reference changes (entities/fields/relationships) that shipped — link to the ERD changelog entry if version was bumped.
- **Deferred / carried over**: Anything planned but not finalized, and why.
- **Related decisions**: Links to [DECISION_LOG.md](DECISION_LOG.md) entries finalized this sprint.
- **Owner**: Who confirmed this sprint's scope as final.
```

---

## Log

<!-- Newest entries go here, directly below this line. -->

### Sprint 2 — 2026-09-09 to 2026-09-09

- **Goal**: Add shift templates and labor regulations, with an activation gate standing in for legal sign-off, plus the available-shift-minutes calculation Feature 05 will consume.
- **Shipped**:
  - `db/schema.sql` + `db/seed_data.sql` extended: `shift_template`, `labor_regulation`, `regulation_shift` tables; seed data pre-activated (2 shift templates, 1 regulation, both linked) so Sprint 3+ demos aren't blocked by the gate.
  - Backend (`/backend`): `ShiftTemplate`/`LaborRegulation`/`RegulationShift` models, schemas, services (`compute_available_minutes` handling multi-regulation most-restrictive-break and overnight/midnight-wrapping shifts), and REST endpoints — create/list/update shift templates, create/list regulations, activate either, attach regulations to shifts, and `GET .../available-minutes`.
  - Activation gate enforced at the point of attachment: an `is_active = false` shift template or regulation cannot be linked via `REGULATION_SHIFT` until explicitly activated.
  - Minimal frontend (`/frontend`): Shifts & Compliance view — shift/regulation tables, attach-regulation and activate actions, live available-minutes display. Manually verified end-to-end in-browser (480 min for the seeded Morning Shift, matching the ERD worked example; 420 min for the overnight Night Shift).
  - 18 automated `pytest` tests in `backend/tests/test_shift_compliance.py`, backfilling the full test case doc as part of this sprint (per the updated CLAUDE.md §6 practice) rather than after the fact.
- **Data model impact**: ERD reference bumped **v2 → v3**: added `is_active`, `activated_by`, `activated_at` to `SHIFT_TEMPLATE` and `LABOR_REGULATION` (Sections 2.6–2.7), implementing the "Legal sign-off before activation" contract (Section 5.2) as an enforced gate. Also retroactively filled in the previously-blank v2.0 changelog entry. See [labor-planning-erd-reference-v2.md](reference/labor-planning-erd-reference-v2.md) §9.
- **Deferred / carried over**: None for BL-2 itself. Flagged for Feature 04 (Sprint 4): its previously-proposed ERD bump is now v3→v4, not v2→v3, since this sprint took v3.
- **Related decisions**: [Sprint 2 approved into Sprint Backlog](DECISION_LOG.md) (2026-09-09).
- **Commit**: `7005cce` on branch `master`, 2026-09-09 — pushed to `https://github.com/adisri94/Labour_Planning_Tool.git` per [CLAUDE.md](../CLAUDE.md) §8.
- **Owner**: Aditya Srivastava

### Sprint 1 (backfill) — 2026-09-09

- **Goal**: Close the automated-testing gap identified after Sprint 1 shipped with only manual verification; make automated testing standard practice for all future sprints.
- **Shipped**:
  - `backend/tests/conftest.py`, `test_master_data.py`, `test_init_db.py` — 19 automated `pytest` tests backfilling 19 of the 20 test cases in [testcases/01-facility-org-master-data.md](testcases/01-facility-org-master-data.md) (TC-5 remains manual/UI-only).
  - `backend/requirements-dev.txt` for test dependencies (`pytest`, `httpx`).
  - [CLAUDE.md](../CLAUDE.md) §6 updated: automated test backfill is now part of every sprint's definition of done.
- **Data model impact**: None.
- **Deferred / carried over**: None — all backend-testable Sprint 1 scenarios are now automated.
- **Related decisions**: [Automated testing backfilled for Sprint 1; made standing practice going forward](DECISION_LOG.md) (2026-09-09) — includes the TC-6 ambiguity found and resolved while writing the tests.
- **Commit**: `942a277` on branch `master`, 2026-09-09 — pushed to `https://github.com/adisri94/Labour_Planning_Tool.git` per [CLAUDE.md](../CLAUDE.md) §8. Also includes the detailed Sprint 2 (BL-2) Feature Document and Test Cases drafted the same session (not yet approved for development).
- **Owner**: Aditya Srivastava

### Sprint 1 — 2026-09-08 to 2026-09-08

- **Goal**: Stand up the Facility & Org Master Data foundation — warehouse/zone/employee/job-role/employee-role CRUD, the first slice of the local SQLite mock data source, and a minimal frontend view.
- **Shipped**:
  - `db/schema.sql` + `db/seed_data.sql` + `db/init_db.py` — bootstrap the local mock data source (1 warehouse, 4 zones, 4 job roles, 12 employees with role certifications).
  - FastAPI backend (`/backend`): `WAREHOUSE`, `ZONE`, `JOB_ROLE`, `EMPLOYEE`, `EMPLOYEE_ROLE` models, services, and REST endpoints (create/list/update warehouses & zones; create/list job roles; create/list/update employees; certify/list employee roles).
  - Service-layer enforcement of the Workforce Master Data Product contract (ERD reference §5.1): active employee must have ≥1 role; `labor_rate > 0`; enumerated `zone_type`/`employee_type`/`employment_status` values validated.
  - Minimal React + Vite frontend (`/frontend`): Warehouse & Zones view, Employees view with role certification and termination actions — manually verified end-to-end in-browser.
  - `README.md` and `.gitignore` added for repo replication.
- **Data model impact**: None — implements ERD reference v2 §2.1–2.5 as-is, no schema changes.
- **Deferred / carried over**: `is_primary` uniqueness constraint (open question, not enforced); final 422 error envelope format (deferred to Feature 10, Sprint 8).
- **Related decisions**: Product Overview approval, Feature Set/MoSCoW, Release Plan, Solution Architecture, and Sprint 1 approval — all in [DECISION_LOG.md](DECISION_LOG.md), entries dated 2026-09-07/2026-09-08.
- **Commit**: `b24f25447f4803c5e5d8dfdc958d5b8076165670` on branch `master`, 2026-09-08 — pushed to `https://github.com/adisri94/Labour_Planning_Tool.git` (new branch) on 2026-09-08 per [CLAUDE.md](../CLAUDE.md) §8.
- **Owner**: Aditya Srivastava
