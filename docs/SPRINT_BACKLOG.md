# Sprint Backlog — Warehouse Labor Planning Tool

Tracks what is committed to the *current* sprint. One section per sprint; keep prior sprints in this file (append-only history) or move them below a "Past Sprints" divider once closed — either way, don't delete them.

Sprint sequence and phase assignment follow [RELEASE_PLAN.md](RELEASE_PLAN.md): Phase 1 (Sprints 1–7, Must Have), Phase 2 (Sprints 8–9, Should Have), Phase 3 (Sprint 10, Could Have) — one feature per sprint. The table below is the planned sequence; a row only becomes an actual committed sprint (moves to "Current Sprint") once its Feature Document, backlog entry, and test cases are approved per the Development Gate.

Development on any item below may start **only after** its Feature Document is approved (see [CLAUDE.md](../CLAUDE.md) Section 7 — Development Gate) and test cases exist in [testcases/](testcases/).

## How to add a sprint entry

```
## Sprint <N> — [YYYY-MM-DD start] to [YYYY-MM-DD end]

**Sprint Goal**: <one sentence>

| Backlog ID | Item | Feature Doc | Test Cases | Approval Status | Dev Status |
|------------|------|--------------|------------|------------------|------------|
| BL-<N> | <title> | [link](features/<slug>.md) | [link](testcases/<slug>.md) | Pending/Approved | Not Started/In Progress/Done |
```

- **Approval Status** must be `Approved` (with sign-off recorded in [DECISION_LOG.md](DECISION_LOG.md)) before **Dev Status** may leave `Not Started`.
- At sprint close, finalize this table and add the corresponding entry to [PRODUCT_LOG.md](PRODUCT_LOG.md).

---

## Planned Sequence (per Release Plan)

| Sprint | Phase | Backlog ID | Feature | Approval Status |
|--------|-------|------------|---------|------------------|
| 1 | Phase 1 (Must) | BL-1 | Facility & Org Master Data | Approved |
| 2 | Phase 1 (Must) | BL-2 | Shift & Compliance Configuration | Approved |
| 3 | Phase 1 (Must) | BL-3 | Demand Signal Ingestion | Pending |
| 4 | Phase 1 (Must) | BL-4 | Task Engine | Pending |
| 5 | Phase 1 (Must) | BL-5 | Labor Requirement Calculation Engine | Pending |
| 6 | Phase 1 (Must) | BL-6 | Employee Shift & Supply Tracking | Pending |
| 7 | Phase 1 (Must) | BL-7 | Labor Plan Matching | Pending |
| 8 | Phase 2 (Should) | BL-10 | Data Product Catalog & API Layer | Pending |
| 9 | Phase 2 (Should) | BL-8 | Governance & Change Management | Pending |
| 10 | Phase 3 (Could) | BL-9 | Observability & Data Health Monitoring | Pending |

## Current Sprint

## Sprint 2 — Phase 1 (Must Have)

**Sprint Goal**: Add shift templates and labor regulations, with an activation gate standing in for legal sign-off, plus the available-shift-minutes calculation Feature 05 will consume — the second slice of the local SQLite mock data source and backend.

| Backlog ID | Item | Feature Doc | Test Cases | Approval Status | Dev Status |
|------------|------|--------------|------------|------------------|------------|
| BL-2 | Shift & Compliance Configuration | [link](features/02-shift-compliance-configuration.md) | [link](testcases/02-shift-compliance-configuration.md) | Approved | Done |

## Past Sprints

### Sprint 1 — Phase 1 (Must Have)

**Sprint Goal**: Stand up the Facility & Org Master Data foundation — warehouse/zone/employee/job-role/employee-role CRUD, the first slice of the local SQLite mock data source, and a minimal frontend view — so every later feature has a trustworthy data foundation to build on.

| Backlog ID | Item | Feature Doc | Test Cases | Approval Status | Dev Status |
|------------|------|--------------|------------|------------------|------------|
| BL-1 | Facility & Org Master Data | [link](features/01-facility-org-master-data.md) | [link](testcases/01-facility-org-master-data.md) | Approved | Done |
