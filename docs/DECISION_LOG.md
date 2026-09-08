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
