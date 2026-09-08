# Release Plan — Warehouse Labor Planning Tool

This document maps the [MoSCoW-prioritized feature set](FEATURE_SET_OVERVIEW.md) onto a phased, multi-release roadmap. It is the authoritative source for "which phase/sprint is a feature in" — [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) and [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md) must stay consistent with it.

## Principles

- **Phases follow MoSCoW priority**: Phase 1 = Must Have, Phase 2 = Should Have, Phase 3 = Could Have. Won't Have items stay out of all phases unless re-prioritized.
- **One feature per sprint.** Each sprint targets exactly one feature from the current phase, developed fully or partially (a feature may span more than one sprint if needed — see Section 4).
- **Sequential within a phase.** Sprint order within a phase follows the feature's position in its dependency chain (see [FEATURE_SET_OVERVIEW.md](FEATURE_SET_OVERVIEW.md) "Suggested sequencing").
- **Gate still applies.** Per [CLAUDE.md](../CLAUDE.md) Section 7, a feature does not enter a sprint until its Feature Document, backlog entry, and test cases are drafted and you've approved them — this plan sequences *intent*, not pre-approval.
- **Each phase is a release.** A phase completing = a release milestone, logged in [PRODUCT_LOG.md](PRODUCT_LOG.md) with its own summary, independent of the sprint-level entries within it.

## Phase 1 — MVP (Must Have)

Goal: get the core demand → task → requirement → supply → plan chain running end-to-end for a single warehouse.

| Sprint | Feature | Backlog ID |
|--------|---------|------------|
| Sprint 1 | [Facility & Org Master Data](features/01-facility-org-master-data.md) | BL-1 |
| Sprint 2 | [Shift & Compliance Configuration](features/02-shift-compliance-configuration.md) | BL-2 |
| Sprint 3 | [Demand Signal Ingestion](features/03-demand-signal-ingestion.md) | BL-3 |
| Sprint 4 | [Task Engine](features/04-task-engine.md) | BL-4 |
| Sprint 5 | [Labor Requirement Calculation Engine](features/05-labor-requirement-calculation.md) | BL-5 |
| Sprint 6 | [Employee Shift & Supply Tracking](features/06-employee-shift-supply-tracking.md) | BL-6 |
| Sprint 7 | [Labor Plan Matching](features/07-labor-plan-matching.md) | BL-7 |

**Phase 1 exit criteria**: a labor plan can be produced end-to-end from ingested demand and configured supply, for at least one warehouse, without manual data patching.

## Phase 2 — First Enhancement (Should Have)

Goal: harden the MVP with governance and a consistent API contract.

| Sprint | Feature | Backlog ID |
|--------|---------|------------|
| Sprint 8 | [Data Product Catalog & API Layer](features/10-data-product-catalog-api-layer.md) | BL-10 |
| Sprint 9 | [Governance & Change Management](features/08-governance-change-management.md) | BL-8 |

Note: 10 is sequenced first in this phase despite being scoped after 08 in the original numbering, because its API/auth conventions are cheapest to formalize before more endpoints accumulate, and it has no feature dependency blocking it.

**Phase 2 exit criteria**: all Phase 1 endpoints conform to the published API contract; `std_time_mins` changes are dual-approved and audited.

## Phase 3 — Second Enhancement (Could Have)

Goal: make the system self-monitoring.

| Sprint | Feature | Backlog ID |
|--------|---------|------------|
| Sprint 10 | [Observability & Data Health Monitoring](features/09-observability-data-health.md) | BL-9 |

**Phase 3 exit criteria**: all five ERD reference §7 health checks are live and alerting.

## Won't Have (this roadmap)

None currently — see [FEATURE_SET_OVERVIEW.md](FEATURE_SET_OVERVIEW.md) Decision options. If a feature is excluded, it moves here with a reason and a link to the [Decision Log](DECISION_LOG.md) entry.

## 4. Partial-feature sprints

If a feature proves too large for one sprint, split it explicitly in [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md) (e.g., "Sprint 4a", "Sprint 4b") rather than silently carrying it over — the split itself is a decision worth a [Decision Log](DECISION_LOG.md) entry noting what was descoped to the next sprint.

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-09-08 | Aditya Srivastava (draft by Claude) | Initial release plan: 3 phases mapped to MoSCoW, one feature per sprint. |
