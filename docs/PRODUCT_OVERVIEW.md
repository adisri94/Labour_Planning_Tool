# Product Overview — Warehouse Labor Planning Tool

- **Status**: Approved (2026-09-07)
- High-level, living description of the product. Update this when the product's purpose, positioning, or scope shifts — not per sprint (see [PRODUCT_LOG.md](PRODUCT_LOG.md) for sprint-level detail).

## 1. Purpose

The Warehouse Labor Planning Tool translates demand signals (forecasts) and actual order data into granular, actionable labor requirements that warehouse managers can use to plan staffing for upcoming shifts. It closes the loop between "how much work is coming" and "how many people, with what skills, do we need, and when" — computing required headcount per zone, job role, shift, date, and time slot, and matching that requirement against actual employee shift supply.

It solves for warehouses that today either staff reactively (after volume spikes hit) or rely on coarse, whole-shift/whole-facility estimates that don't reflect zone-level or intra-shift variation in demand.

## 2. Positioning

Per [CLAUDE.md](../CLAUDE.md) Section 1, this tool is a **whitespace filler**, not a replacement for the enterprise systems a Retail/CG warehouse already runs:

- **WMS** (e.g., Manhattan Associates, Blue Yonder) — remains the system of record for orders, inventory, and warehouse execution. This tool consumes order/order-line data from it rather than duplicating it.
- **WFM/HCM** (e.g., Workday) — remains the system of record for employee master data, absence, and payroll. This tool consumes employee/role data and produces labor requirements/plans that could feed back into scheduling, but does not replace HCM.
- **Rostering tools** — remain responsible for the final published roster in many shops; this tool's `LABOR_PLAN` output is the recommended staffing, which may hand off to a rostering system rather than being the system employees see.
- **SAP** — a likely source for org/master data and cost-rate integration in some deployments.

Data formats and integration points should stay close to what these systems already emit (per Initiative Objectives: MAWM/Blue Yonder–style WMS exports, SAP, Workday), so the tool can slot into an existing stack with low integration cost.

**What this product is not**: a full WMS, a full HCM/payroll system, or a scheduling/rostering system of record. It is the analytical layer that sits between demand/order data and staffing decisions.

## 3. Target Users / Personas

| Persona | Needs from this tool |
|---|---|
| **Warehouse Manager** | Zone-level, shift-level headcount requirements they can act on for the next shift(s); visibility into whether current employee shifts cover the requirement; alerts on unconfirmed plans close to shift start. |
| **Labor Planning PM / Product Owner** | Confidence that requirements are computed correctly and consistently; governance over changes to standard times and regulations; sprint-level visibility into what's shipped. |
| **Industrial Engineering (IE)** | Ownership and approval authority over `TASK_TYPE.std_time_mins` — the core multiplier in the headcount formula. |
| **Ops Analytics / Finance** | Access to labor plan and cost data (via `JOB_ROLE.labor_rate`) for cost reporting and variance analysis. |
| **Demand Planning team** | Ownership of forecast freshness and quality; consumers of forecast-driven requirement output as a feedback loop. |
| **Future consumers: AI/agentic systems** | Structured, discoverable data products (per Section 5 of this doc and the ERD reference) that can be consumed programmatically, not just via UI. |

## 4. Scope

### In scope (current horizon)

- Modeling and ingesting demand signals: `DEMAND_FORECAST` and confirmed `ORDER`/`ORDER_LINE` data.
- Translating demand into atomic units of work (`TASK_TYPE`, `TASK`) at the zone level.
- Computing labor requirements (`LABOR_REQUIREMENT`) per zone, role, shift, date, and time slot using the standard headcount formula (see [CLAUDE.md](../CLAUDE.md) Section 3.2).
- Modeling labor supply (`EMPLOYEE`, `EMPLOYEE_ROLE`, `SHIFT_TEMPLATE`, `EMPLOYEE_SHIFT`) and regulatory constraints (`LABOR_REGULATION`, `REGULATION_SHIFT`).
- Producing a matched labor plan (`LABOR_PLAN`) that allocates available employee shifts against requirements.
- Governance and observability around the model's most consequential fields (e.g., `std_time_mins`) and data products, per the ERD reference Sections 5–7.
- Incremental delivery: each release adds capability rather than attempting a single big-bang launch. Concretely, this product ships as three MoSCoW-aligned phases/releases — see [RELEASE_PLAN.md](RELEASE_PLAN.md): Phase 1 (Must Have — MVP), Phase 2 (Should Have — first enhancement), Phase 3 (Could Have — second enhancement), each broken into one-feature-per-sprint increments.

### Out of scope / explicitly deferred

- Being the system of record for orders, inventory, employee master data, or payroll — those remain owned by WMS/WFM/HCM systems this tool integrates with.
- Publishing the final employee-facing roster/schedule (rostering tool territory), unless a future feature explicitly extends into that.
- Real-time execution tracking beyond what's needed for post-shift variance (`EMPLOYEE_SHIFT.actual_start/actual_end`).
- Any capability not yet captured as an approved Feature Document — see [CLAUDE.md](../CLAUDE.md) Section 7 (Development Gate). This list will grow as specific features are scoped and rejected/deferred; deferred items should also be tracked in [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md).

## 5. Key Capabilities

Mapped to the three logical layers in the [ERD reference](reference/labor-planning-erd-reference-v2.md):

| Layer | Capability |
|---|---|
| **Input** | Facility/org modeling (warehouse, zone, employee, job role, shift template, labor regulation); demand signal ingestion (forecast, order, order line). |
| **Task** | Definition of repeatable work with engineered standard times (`TASK_TYPE`); instantiation of atomic work units from either actual orders or forecasts (`TASK`). |
| **Output** | Headcount requirement calculation (`LABOR_REQUIREMENT`); supply-side shift tracking (`EMPLOYEE_SHIFT`); demand-to-supply matching (`LABOR_PLAN`). |

Cross-cutting capabilities (from the ERD reference Sections 5–7): data product ownership/SLAs, governance and change management for schema and critical fields, and automated observability/health checks.

## 6. Success Metrics

- **Requirement lead time**: `LABOR_REQUIREMENT` reaches `confirmed` status ≥12 hours before shift start (per the Labor Plan Data Product SLA).
- **Plan confirmation rate**: proportion of `LABOR_PLAN` records reaching `confirmed` before shift start; inverse of the "unconfirmed plan" observability check.
- **Headcount variance**: difference between `planned_headcount` and actual post-shift attendance/output, tracked via `EMPLOYEE_SHIFT` variance logging.
- **Forecast quality**: `DEMAND_FORECAST.confidence_score` distribution and freshness (staleness < 2 hours) as a leading indicator of requirement accuracy.
- **Governance adherence**: zero un-approved changes to `std_time_mins` (per the drift check in the ERD reference Section 7).
- **Delivery cadence**: features shipped per sprint against what was committed in [SPRINT_BACKLOG.md](SPRINT_BACKLOG.md), tracked in [PRODUCT_LOG.md](PRODUCT_LOG.md).

## 7. Related Documents

- [CLAUDE.md](../CLAUDE.md) — standing engineering/process rules for this repo
- [ERD Reference](reference/labor-planning-erd-reference-v2.md) — authoritative data model
- [Initiative Objectives](reference/Labor%20Planning%20Tool%20Development%20Initiative%20Objectives.docx) — original product/engineering mandate
- [Feature Documents](features/)
- [Feature Set Overview / MoSCoW](FEATURE_SET_OVERVIEW.md)
- [Release Plan](RELEASE_PLAN.md)
- [Solution Architecture](SOLUTION_ARCHITECTURE.md)
- [Product Backlog](PRODUCT_BACKLOG.md)
- [Sprint Backlog](SPRINT_BACKLOG.md)
- [Decision Log](DECISION_LOG.md)
- [Product Log](PRODUCT_LOG.md)

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-09-07 | Aditya Srivastava (draft by Claude) | Initial draft, derived from Initiative Objectives and ERD reference v2. Pending approval. |
