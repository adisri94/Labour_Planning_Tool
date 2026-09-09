# Product Backlog — Warehouse Labor Planning Tool

The full, prioritized list of features/capabilities under consideration or planned for this product. Items move from here into a [Sprint Backlog](SPRINT_BACKLOG.md) once selected for a sprint, and get a full [Feature Document](features/) once scoped in detail. Phase/sprint assignment follows the [Release Plan](RELEASE_PLAN.md), which in turn follows the [MoSCoW analysis](FEATURE_SET_OVERVIEW.md).

## How to add an item

```
| ID | Title | Priority | MoSCoW | Phase | Status | Feature Doc | Notes |
|----|-------|----------|--------|-------|--------|--------------|-------|
| BL-<N> | <short title> | High/Med/Low | Must/Should/Could/Won't | Phase 1/2/3 | Backlog/Scoped/In Sprint/Done | [link](features/<slug>.md) | |
```

- **Status** values: `Backlog` (not yet scoped) → `Scoped` (feature doc drafted, pending approval) → `In Sprint` (approved, pulled into a sprint) → `Done` (shipped, logged in [PRODUCT_LOG.md](PRODUCT_LOG.md)).
- Nothing moves to `In Sprint` without an approved Feature Document (see [CLAUDE.md](../CLAUDE.md) Section 7 — Development Gate).

## Backlog

| ID | Title | Priority | MoSCoW | Phase | Status | Feature Doc | Notes |
|----|-------|----------|--------|-------|--------|--------------|-------|
| BL-1 | Facility & Org Master Data | High | Must | Phase 1 | Done | [link](features/01-facility-org-master-data.md) | Foundational — most other features depend on this. Shipped Sprint 1 (2026-09-08). |
| BL-2 | Shift & Compliance Configuration | High | Must | Phase 1 | Scoped | [link](features/02-shift-compliance-configuration.md) | Provides `available_shift_minutes` input to requirement calc. Detailed with test cases (2026-09-08); proposes ERD v3 bump (`is_active`/`activated_by`/`activated_at`); pending approval. |
| BL-3 | Demand Signal Ingestion | High | Must | Phase 1 | Scoped | [link](features/03-demand-signal-ingestion.md) | Forecast + order/order-line ingestion. |
| BL-4 | Task Engine (Task Type & Task Generation) | High | Must | Phase 1 | Scoped | [link](features/04-task-engine.md) | Proposes ERD v3 bump (task_type_change_log). |
| BL-5 | Labor Requirement Calculation Engine | High | Must | Phase 1 | Scoped | [link](features/05-labor-requirement-calculation.md) | Core headcount formula. |
| BL-6 | Employee Shift & Supply Tracking | High | Must | Phase 1 | Scoped | [link](features/06-employee-shift-supply-tracking.md) | Supply-side counterpart to requirements. |
| BL-7 | Labor Plan Matching | High | Must | Phase 1 | Scoped | [link](features/07-labor-plan-matching.md) | Primary consumer-facing output. |
| BL-10 | Data Product Catalog & API Layer | Medium | Should | Phase 2 | Scoped | [link](features/10-data-product-catalog-api-layer.md) | Sequenced first in Phase 2 — cheapest to formalize before endpoints accumulate. |
| BL-8 | Governance & Change Management | Medium | Should | Phase 2 | Scoped | [link](features/08-governance-change-management.md) | Cross-cutting; pairs with BL-4's ERD bump. |
| BL-9 | Observability & Data Health Monitoring | Medium | Could | Phase 3 | Scoped | [link](features/09-observability-data-health.md) | Implements ERD reference §7 checks. |
