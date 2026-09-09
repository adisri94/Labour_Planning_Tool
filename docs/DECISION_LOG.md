# Decision Log — Warehouse Labor Planning Tool

This document records every key decision made and finalized during the development of this project — product scope calls, architecture choices, data model changes, and options that were evaluated and rejected. It is the audit trail referenced by [CLAUDE.md](../CLAUDE.md) Section 5 (Documentation Discipline).

Add a new entry whenever a decision is finalized — not while it's still being debated. Keep entries append-only; if a decision is later reversed, add a new entry that supersedes it rather than editing history.

## How to add an entry

Copy the template below, fill it in, and append it under "Log" in reverse-chronological order (newest on top).

```
### [YYYY-MM-DD] <Short decision title>

- **Status**: Decided | Superseded by [#N](#) 
- **Context**: What prompted this decision — the problem or question being resolved.
- **Options considered**: Brief list of alternatives evaluated, with why each was or wasn't chosen.
- **Decision**: The choice that was finalized.
- **Consequences**: What this affects downstream (schema, APIs, other decisions), and any follow-up actions.
- **Owner**: Who made/approved the call.
```

---

## Log

<!-- Newest entries go here, directly below this line. -->

### [2026-09-10] Demo seed data re-localized from India to the US

- **Status**: Decided
- **Context**: The demo warehouse, workforce, and labor regulation were originally seeded with India-specific context (Mumbai FC-1, Asia/Kolkata timezone, Indian employee names, and the Indian Factories Act 1948 as the seeded `LABOR_REGULATION`). User asked to re-localize the demo to be relevant for US-based clients instead.
- **Options considered**: N/A — direct instruction to change locale; only judgment calls were on specific values (see Consequences).
- **Decision**: Updated `db/seed_data.sql` (Sprint 1 and Sprint 2 sections): warehouse → "Chicago FC-1", "Chicago, IL, USA", `America/Chicago`; 12 employee names → US-typical names (IDs, hire dates, statuses, and role assignments left unchanged); `JOB_ROLE.labor_rate` → plausible USD hourly wages ($18.50–$24.00, previously values that read as INR); `LABOR_REGULATION` → renamed `reg-factories-act`/"Factories Act 1948" to `reg-flsa`/"Fair Labor Standards Act (FLSA)", `region` → "USA", `max_hours_per_day` 9→8 and `max_hours_per_week` 48→40 (FLSA's actual overtime threshold). `break_interval_mins` and `overtime_multiplier` (1.5x) left unchanged — 60-minute break preserves the ERD reference §4 worked example's 540→480 minute result, and 1.5x happens to also be the real FLSA overtime multiplier. Updated the two dependent test files (`backend/tests/conftest.py`, `test_master_data.py`, `test_shift_compliance.py`) and the seed-data descriptions in Feature Documents 01 and 02 to match. The authoritative [ERD reference](../reference/labor-planning-erd-reference-v2.md)'s illustrative examples (e.g., "Mumbai FC-1" in the WAREHOUSE attribute description) were deliberately left untouched — those are generic placeholder examples in the schema documentation, not the actual seed data, and changing them isn't necessary for this request.
- **Consequences**: All 36 automated tests still pass unchanged (no test asserted the old India-specific literal values except the regulation id/location fields, which were updated). Anyone running `python db/init_db.py --reset` now gets a US-localized demo. No schema/entity change — no ERD version bump required.
- **Owner**: Aditya Srivastava

### [2026-09-09] ERD reference bumped to v3; Sprint 2 development completed

- **Status**: Decided
- **Context**: Sprint 2 (BL-2) development completed: `db/schema.sql`/`seed_data.sql` extended, FastAPI backend and minimal frontend built, and 18 automated `pytest` tests written and passing, backfilling the full test case doc as part of the sprint itself (per the CLAUDE.md §6 practice established 2026-09-09).
- **Options considered**: N/A — applying the previously-approved ERD v3 bump independently of Feature 04's proposed change, as flagged when Sprint 2 was approved into the backlog.
- **Decision**: Applied ERD v3: added `is_active`/`activated_by`/`activated_at` to `SHIFT_TEMPLATE` and `LABOR_REGULATION` in [labor-planning-erd-reference-v2.md](../reference/labor-planning-erd-reference-v2.md) §2.6–2.7, updated the §5.2 quality contract description, and filled in the previously-blank v2.0 changelog entry retroactively (§9) alongside the new v3.0 entry. Feature 04's Feature Document updated to note its own proposed bump is now v3→v4, not v2→v3.
- **Consequences**: All backend acceptance criteria verified via curl and the automated test suite (36/36 passing repo-wide); the frontend's Shifts & Compliance view verified live in-browser, matching the ERD's worked example (480 available minutes for the Morning Shift) and correctly handling the overnight Night Shift's midnight wrap (420 minutes). Not yet committed/pushed — pending separate explicit confirmation per [CLAUDE.md](../CLAUDE.md) §8.
- **Owner**: Aditya Srivastava

### [2026-09-09] Sprint 2 (BL-2, Shift & Compliance Configuration) approved into Sprint Backlog

- **Status**: Decided
- **Context**: [Feature Document](../docs/features/02-shift-compliance-configuration.md) (4 user stories, per-story acceptance criteria, DDL sketch, available-minutes calculation rule) and [Test Cases](../docs/testcases/02-shift-compliance-configuration.md) (18 test cases, TC-1–TC-18) were drafted for BL-2 per the [Release Plan](RELEASE_PLAN.md)'s Sprint 2 slot, including a resolution of the Sprint-1-era open question on how legal sign-off is recorded (an `is_active`/`activated_by`/`activated_at` gate on `SHIFT_TEMPLATE` and `LABOR_REGULATION`).
- **Options considered**: N/A — direct review and approval of the completed document set.
- **Decision**: Approved as-is, including the proposed ERD v3 bump for the new gate fields. Sprint 1 moved to "Past Sprints" (Done) and Sprint 2 moved into "Current Sprint" in [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md); Feature Document and Test Cases status flipped to `Approved`; [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) BL-2 status flipped to `In Sprint`.
- **Consequences**: Development on BL-2 may now begin per the Development Gate (CLAUDE.md §7), including extending `db/schema.sql`/`seed_data.sql`, the FastAPI backend, and the minimal frontend for shift templates and regulations. Per [CLAUDE.md](../CLAUDE.md) §6 (updated 2026-09-09), automated `pytest` tests backfilling the test case doc are required as part of this sprint's definition of done, not a follow-up. The [ERD reference](../reference/labor-planning-erd-reference-v2.md) itself still needs its changelog (§9) updated with the v3 entry once the schema change is implemented — tracked as a to-do for this sprint's work, not deferred.
- **Owner**: Aditya Srivastava

### [2026-09-09] Automated testing backfilled for Sprint 1; made standing practice going forward

- **Status**: Decided
- **Context**: Sprint 1 had only been manually verified (curl + browser click-through), not covered by an automated test suite — a gap against [CLAUDE.md](../CLAUDE.md) §2's "production-grade... tests" standard. User asked to backfill Sprint 1 with automated tests first, then make automated testing standard practice going forward.
- **Options considered**: N/A — direct instruction on ordering (backfill first, then codify the practice).
- **Decision**: Added `pytest`-based automated tests in `backend/tests/` (`test_master_data.py`, `test_init_db.py`, `conftest.py` with an isolated in-memory SQLite fixture — deliberately not the demo `db/labor_planning.db`) covering 19 of the 20 test cases in [testcases/01-facility-org-master-data.md](../testcases/01-facility-org-master-data.md) (TC-5 remains manual/browser-only). Added `backend/requirements-dev.txt` for `pytest`/`httpx`. Codified in [CLAUDE.md](../CLAUDE.md) §6: automated tests are part of every sprint's definition of done going forward, backfilled from the test case doc before a sprint's Dev Status is marked `Done`.
- **Consequences**: Writing TC-6 as a real test surfaced a genuine ambiguity — the Feature Document's US-2 first acceptance criterion implied any "valid" employee payload (including `employment_status: active`) could be created, but the actual (already-approved, running) implementation enforces the ≥1-role contract at creation time too, so an active employee with zero roles is rejected even on `POST /employees`. Resolved by correcting TC-6 to use `employment_status: on_leave` and documenting the resolution inline in both the test case doc and the test's own comment, rather than silently patching around it. All 19 automated tests pass.
- **Owner**: Aditya Srivastava

### [2026-09-08] Sprint 1 development approved and committed

- **Status**: Decided
- **Context**: Sprint 1 (BL-1) development completed and verified end-to-end (backend API acceptance criteria tested via curl; frontend flows — zone listing, role certification, employee termination — verified live in-browser). All planning docs (Product Overview, Feature Set Overview/MoSCoW, Release Plan, Solution Architecture, Feature Documents 01–10, Test Cases 01) and the implementation were ready for a first commit.
- **Options considered**: N/A — direct approval to commit the completed work.
- **Decision**: Approved. Committed to local git repo as commit `b24f25447f4803c5e5d8dfdc958d5b8076165670` on branch `master` (2026-09-08), containing the full planning doc set plus Sprint 1 implementation (`db/`, `backend/`, `frontend/`, `README.md`, `.gitignore`). Not yet pushed to the remote — push requires separate explicit confirmation per [CLAUDE.md](../CLAUDE.md) §8.
- **Consequences**: This is the repo's root commit — no prior history exists. Generated artifacts (`backend/.venv/`, `frontend/node_modules/`, `db/labor_planning.db`) were excluded via `.gitignore` and are not part of the commit.
- **Owner**: Aditya Srivastava

### [2026-09-08] Sprint 1 (BL-1, Facility & Org Master Data) approved into Sprint Backlog

- **Status**: Decided
- **Context**: [Feature Document](../docs/features/01-facility-org-master-data.md) (with 4 detailed user stories and per-story acceptance criteria) and [Test Cases](../docs/testcases/01-facility-org-master-data.md) (20 test cases, TC-1–TC-20) were drafted for BL-1 per the [Release Plan](RELEASE_PLAN.md)'s Sprint 1 slot.
- **Options considered**: N/A — direct review and approval of the completed document set.
- **Decision**: Approved as-is. Sprint 1 moves from "Planned Sequence" to "Current Sprint" in [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md); Feature Document and Test Cases status flipped to `Approved`; [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) BL-1 status flipped to `In Sprint`.
- **Consequences**: Development on BL-1 (warehouse/zone/employee/job-role/employee-role CRUD, `db/schema.sql`+`seed_data.sql` first slice, minimal frontend view) may now begin per the Development Gate (CLAUDE.md §7). Two open questions remain unresolved but non-blocking: `is_primary` uniqueness constraint, and the 422 error envelope format (deferred to Feature 10/Sprint 8).
- **Owner**: Aditya Srivastava

### [2026-09-08] Solution architecture: local SQLite mock data source, FastAPI backend, minimal React frontend

- **Status**: Decided
- **Context**: Needed a runnable architecture for demo/show-and-tell that doesn't require a real WMS/HCM/OMS integration or external DB server, while staying credible per [CLAUDE.md](../CLAUDE.md) §2 (tooling realism, UI/backend separation).
- **Options considered**: DB — SQLite (chosen, zero-setup) vs. PostgreSQL (closer to prod, but requires a local server — more friction for repo replication). Backend — Python/FastAPI (chosen, auto-generates OpenAPI matching Feature 10) vs. Node/Express. Frontend — API-only vs. minimal UI now (chosen, gives the demo something visual).
- **Decision**: Local mock data source is a single-file SQLite DB (`labor_planning.db`), created and seeded by checked-in `db/schema.sql` + `db/seed_data.sql` (run via `db/init_db.py`) — explicitly labeled as standing in for real WMS/WFM/OMS feeds. Backend is Python + FastAPI with SQLAlchemy. Frontend is a minimal React + Vite SPA. Full detail in new [SOLUTION_ARCHITECTURE.md](SOLUTION_ARCHITECTURE.md).
- **Consequences**: `db/schema.sql`/`seed_data.sql` and backend models are built incrementally per feature sprint (starting Sprint 1 / BL-1), not as one upfront schema dump. SQLAlchemy chosen specifically so swapping SQLite for Postgres later (real deployment) is a config change, not a rewrite. No auth is assumed for the laptop-demo scenario — flagged as still open in Feature 10.
- **Owner**: Aditya Srivastava

### [2026-09-08] Multi-release phasing: MoSCoW-aligned phases, one feature per sprint

- **Status**: Decided
- **Context**: With 10 features scoped and MoSCoW-prioritized in [FEATURE_SET_OVERVIEW.md](FEATURE_SET_OVERVIEW.md), the user asked for a formal multi-release structure rather than one flat backlog.
- **Options considered**: N/A — direct instruction on structure (phase-per-MoSCoW-tier, one feature per sprint).
- **Decision**: Three release phases, each corresponding to a MoSCoW tier: Phase 1 = Must Have (Sprints 1–7: BL-1 through BL-7, in dependency order), Phase 2 = Should Have (Sprints 8–9: BL-10 then BL-8), Phase 3 = Could Have (Sprint 10: BL-9). Each sprint targets exactly one feature, which may be developed fully or partially within that sprint. Documented in new [RELEASE_PLAN.md](RELEASE_PLAN.md), with [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) and [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md) updated to carry Phase/MoSCoW columns and the planned sprint sequence.
- **Consequences**: BL-10 (API Layer) is sequenced ahead of BL-8 (Governance) within Phase 2 despite its higher original feature number, because it's cheapest to formalize before more endpoints exist and has no feature dependency blocking it. The Development Gate (CLAUDE.md §7) still applies per-sprint — this plan sequences intent, not pre-approval.
- **Owner**: Aditya Srivastava

### [2026-09-07] Product Overview approved

- **Status**: Decided
- **Context**: Initial [Product Overview](PRODUCT_OVERVIEW.md) drafted from the Initiative Objectives and ERD reference v2, covering purpose, positioning, personas, scope, capabilities, and success metrics.
- **Options considered**: N/A — first-pass draft reviewed as a whole.
- **Decision**: Product Overview approved as-is. Feature Documents to be drafted next for the full feature set needed to meet the stated objectives, per [CLAUDE.md](../CLAUDE.md) Section 7 (Development Gate).
- **Consequences**: Product Overview status flipped to `Approved`. No code changes yet — Feature Documents, Product/Sprint Backlog entries, and test cases still required before development starts.
- **Owner**: Aditya Srivastava
