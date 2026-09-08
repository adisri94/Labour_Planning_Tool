# CLAUDE.md — Warehouse Labor Planning Tool

This file is the standing reference for every "vibe code" prompt used to develop the Labor Planning Tool. Read it before generating, modifying, or reviewing any code, schema, or documentation in this repository. It distills the two source-of-truth documents in [docs/reference/](docs/reference/):

- [Labor Planning Tool Development Initiative Objectives.docx](docs/reference/Labor%20Planning%20Tool%20Development%20Initiative%20Objectives.docx) — the product/engineering mandate (the "why" and "how we build").
- [labor-planning-erd-reference-v2.md](docs/reference/labor-planning-erd-reference-v2.md) — the data model (the "what we build on"), currently v2.

It also governs [docs/DECISION_LOG.md](docs/DECISION_LOG.md) — the running record of every key decision finalized during development (see Section 5) — and [docs/PRODUCT_LOG.md](docs/PRODUCT_LOG.md) — the record of what was finalized and shipped at the end of each sprint (see Section 5).

**Hard rule: no development work (writing or modifying application code) starts until the user has explicitly approved the planning documents for that work — see Section 7 (Development Gate). This is a standing rule for all future prompts, not a one-time instruction.**

If any generated code, schema, or design contradicts these documents, the documents win — flag the conflict and ask before deviating.

---

## 1. Product Positioning (from Initiative Objectives)

- This tool is a **whitespace filler** that complements — not replaces — the SaaS systems a Retail/CG warehouse already runs: WMS, WFM/HCM, rostering tools. Design integration points and data formats to be compatible with common inputs from these systems (e.g., Manhattan/Blue Yonder-style WMS exports, SAP, Workday).
- Ship as **multiple incremental releases** with steadily improving features, not one monolithic build. When proposing scope for a change, default to the smallest coherent increment.
- Treat the product as a **Data Product application**: every entity and pipeline must have a clear answer to "what KPI/feature/capability does this data drive?" Favor designs where data is ready-for-consumption by downstream AI/agentic initiatives, not just by this app's own UI.

## 2. Engineering Standards (Production-Grade Code)

Apply these to all code generated for this project, not just when explicitly asked:

- **Architecture**: strict separation of UI and backend; backend exposed via well-defined APIs; consider microservice boundaries where they map to the data-product boundaries in Section 4 below.
- **Modularity & maintainability**: small, composable modules; avoid god-files/god-classes; prefer explicit interfaces over implicit coupling.
- **Documentation**: every non-trivial module, API, and schema change should be documented inline and in repo docs — see Section 5.
- **Security**: follow security-compliant practices by default (input validation, no secrets in code, least-privilege data access).
- **Coding standards**: hold generated code to the same bar as manually-written production code — proper naming, error handling, tests — not "demo-quality" shortcuts.
- **Tooling realism**: use near-production-grade tools and formats (real databases, real API contracts, JSON/IDOC-style payloads) instead of toy stand-ins, so the tool is credible against real WMS/WFM integrations.
- **Agentic-first**: where reasonable, design features/data so they can be driven or consumed by agents (clear schemas, discoverable APIs, structured outputs), not just human UI flows.

## 3. Data Model — Authoritative Source

The full entity/attribute/relationship catalogue lives in [labor-planning-erd-reference-v2.md](docs/reference/labor-planning-erd-reference-v2.md). Do not invent entities or fields ad hoc — extend that document first (with a changelog entry per Section 6.2 of it), then implement.

### 3.1 Three logical layers

| Layer | Entities |
|---|---|
| **Input** | WAREHOUSE, ZONE, EMPLOYEE, JOB_ROLE, EMPLOYEE_ROLE, SHIFT_TEMPLATE, LABOR_REGULATION, REGULATION_SHIFT, DEMAND_FORECAST, ORDER, ORDER_LINE |
| **Task** | TASK_TYPE, TASK |
| **Output** | LABOR_REQUIREMENT, EMPLOYEE_SHIFT, LABOR_PLAN |

### 3.2 Core calculation (never reimplement differently without updating the ERD doc)

```
total_task_minutes   = Σ (task.quantity × task_type.std_time_mins)   per zone + role + shift + slot
required_headcount   = CEIL( total_task_minutes ÷ available_shift_minutes )
```

- `TASK_TYPE.std_time_mins` is the single most consequential field in the model — treat changes to it as governed (see Section 6 of the ERD doc: IE + Labor Planning PM approval, `change_log` audit trail, auto-recompute of the next 14 days of LABOR_REQUIREMENT for the affected zone, DB constraint `std_time_mins > 0`).
- Tasks originate from either `ORDER_LINE` (actual, `source_type = actual`) or `DEMAND_FORECAST` (`source_type = forecast`); LABOR_REQUIREMENT can be `forecast`, `actual`, or `blended`.
- `LABOR_PLAN` is the demand↔supply match: it links a `LABOR_REQUIREMENT` to an `EMPLOYEE_SHIFT`. Sum of `planned_headcount` across plans for a requirement must equal that requirement's `required_headcount`.

### 3.3 Key invariants to preserve in any implementation

- Every ZONE belongs to exactly one WAREHOUSE; every TASK_TYPE belongs to exactly one ZONE.
- EMPLOYEE↔JOB_ROLE is many-to-many via EMPLOYEE_ROLE (`is_primary` flag distinguishes default role).
- LABOR_REGULATION↔SHIFT_TEMPLATE is many-to-many via REGULATION_SHIFT (multiple regulations can govern one shift).
- `LABOR_REQUIREMENT.required_headcount` must always be >= 1.
- `EMPLOYEE_SHIFT.actual_start`/`actual_end` populated within 30 minutes of shift completion (for variance analysis).

### 3.4 Data Products (own SLAs/quality contracts — enforce, don't just store)

| Data Product | Entities | Notable contract |
|---|---|---|
| Workforce Master | WAREHOUSE, ZONE, EMPLOYEE, JOB_ROLE, EMPLOYEE_ROLE | `employment_status` terminations reflected within 30 min; every active employee has ≥1 EMPLOYEE_ROLE |
| Shift & Compliance | SHIFT_TEMPLATE, LABOR_REGULATION, REGULATION_SHIFT | Changes require Legal sign-off before activation |
| Demand Signals | DEMAND_FORECAST, ORDER, ORDER_LINE | Forecasts stale after 2h; new orders visible within 15 min; `confidence_score` ∈ [0,1] |
| Labor Plan (primary output) | LABOR_REQUIREMENT, EMPLOYEE_SHIFT, LABOR_PLAN | Requirement `confirmed` ≥12h before shift start; plan `confirmed` before shift start |

When building features against these entities, surface/validate the relevant contract rather than silently trusting the data.

## 4. Change Management for the Data Model

- Any structural change (add/rename column, change type, deprecate a relationship) requires: consumer notice ≥5 business days ahead of breaking changes, backward compatibility for ≥1 full shift cycle (24h) on non-breaking additions, and a changelog entry in the ERD doc (version bump, date, author, description).
- When a vibe-code prompt implies a schema change, propose the ERD doc update alongside the code change — don't let the two drift apart.

## 5. Documentation Discipline (from Initiative Objectives, Section 4)

For any non-trivial change, capture:
- What was built and why (the decision, not just the diff).
- Options evaluated and rejected, with rationale.
- Any deviation from this CLAUDE.md or the ERD reference, and why.

**Every key decision that gets finalized during development — product scope, architecture, tooling, data model changes, anything with lasting consequences — must be logged in [docs/DECISION_LOG.md](docs/DECISION_LOG.md)** using the template at the top of that file. Log it when the decision is actually settled, not while still under discussion. When a prompt in this repo results in a finalized decision, append the entry to the decision log as part of that same piece of work, don't defer it.

**At the end of each development sprint, once its scope is finalized, log what shipped in [docs/PRODUCT_LOG.md](docs/PRODUCT_LOG.md)** using the template at the top of that file, including any data model impact and links to the decision-log entries settled during that sprint.

This project is also meant to produce a reusable **framework/playbook for AI-assisted builders** — write documentation assuming a future AI agent (not just a human) is the reader.

## 6. Working Agreement for Prompts in This Repo

- Default to the smallest correct increment; don't gold-plate.
- Check [labor-planning-erd-reference-v2.md](docs/reference/labor-planning-erd-reference-v2.md) before adding/renaming any entity, field, or relationship.
- Preserve the input → task → output layering; don't let output-layer entities be computed from anything other than TASK/DEMAND_FORECAST aggregation as defined above.
- Keep UI and backend concerns separated at all times; no direct UI-to-DB access.
- Flag any place where a prompt's request conflicts with Sections 1–5 above instead of silently reinterpreting scope.

## 7. Development Gate — Documentation Before Code

No application code, schema migration, or infrastructure change is written until the corresponding planning documents exist **and the user has explicitly approved them**. This applies to every unit of work, no matter how small it seems — do not skip the gate because a change "looks trivial."

### 7.1 Required documents, in order

1. **[Product Overview](docs/PRODUCT_OVERVIEW.md)** — must exist and reflect current scope before any feature work begins. Update it when a feature changes overall product scope/positioning.
2. **[Feature Document](docs/features/)** — one per feature, from [TEMPLATE_FEATURE.md](docs/features/TEMPLATE_FEATURE.md). Covers problem, scope, user stories, data model impact, API design, acceptance criteria.
3. **[Product Backlog](docs/PRODUCT_BACKLOG.md)** — the feature must be entered here with status `Scoped` once its Feature Document is drafted.
4. **[Sprint Backlog](docs/SPRINT_BACKLOG.md)** — the feature must be pulled into a named sprint entry before work starts on it.
5. **[Test Cases](docs/testcases/)** — one file per feature, from [TEMPLATE_TESTCASES.md](docs/testcases/TEMPLATE_TESTCASES.md), covering happy path, edge cases, failure modes, and any relevant Data Product quality contracts (ERD reference Sections 5 & 7).

### 7.2 Approval checkpoint

- Once all five documents above are drafted for a piece of work, present them to the user for review as a set.
- Development may begin **only after** the user gives explicit approval (e.g., "approved", "go ahead", "start development"). Silence, a topic change, or approval of only part of the set does not count as approval.
- Record the approval as a [Decision Log](docs/DECISION_LOG.md) entry, and flip the Feature Document's status to `Approved` and the Product Backlog row to `In Sprint`.
- If the user requests changes mid-review, revise the documents and re-present before treating anything as approved.

### 7.3 Exceptions

- Pure documentation edits, fixing typos in these planning docs, and read-only investigation/research do not require this gate.
- If the user explicitly instructs skipping the gate for a specific, narrow request, follow that instruction for that request only — the gate still applies to everything else by default.

## 8. Repo Replication

Once a development change or update is approved per Section 7 and completed, the entire repository must be replicated (committed and pushed) to the remote:

```
https://github.com/adisri94/Labour_Planning_Tool.git
```

- This is a standing rule for all future approved work — treat every approved sprint/feature completion as implying a push to this remote, not just a local commit.
- Pushing remains an explicit-permission, per-action step: confirm with the user (repo, branch, and commit summary) before each actual push, even though the rule to push after approval is standing.
- If the remote doesn't yet have a matching branch, create it; don't force-push over existing history without explicit user confirmation.
- Record the push (commit hash, branch, date) in [docs/PRODUCT_LOG.md](docs/PRODUCT_LOG.md) for that sprint's entry.
