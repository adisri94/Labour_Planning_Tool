# Feature Document — Demand Signal Ingestion

- **Status**: Draft — Pending Approval
- **Approved by**: —
- **Related sprint**: TBD — [SPRINT_BACKLOG.md](../SPRINT_BACKLOG.md)
- **Related backlog item(s)**: BL-3 — [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)

## 1. Problem / Goal

Labor requirements need to be driven by both forward-looking forecasts and confirmed orders. This feature ingests and stores both, forming the Demand Signals data product — the highest-leverage input for requirement accuracy.

## 2. Scope

### In scope

- Ingestion and storage of `DEMAND_FORECAST` (from OMS feeds/statistical models) and `ORDER`/`ORDER_LINE` (from WMS/OMS).
- Enforcement of Demand Signals quality contracts (ERD reference §5.3): forecast staleness (>2h flagged), new orders visible within 15 minutes of OMS receipt, `confidence_score` ∈ [0,1], `expected_ship_date` non-null for `received`/`in_progress` orders, `quantity > 0`, no duplicate `order_id`.
- Basic dedup/upsert semantics for repeated feed deliveries.

### Out of scope

- The statistical forecasting model itself (treated as an external signal source, `signal_source`); this feature only ingests its output.
- Order fulfillment execution (remains WMS territory).

## 3. User Stories / Requirements

- As a demand planner, I want forecast records ingested per warehouse/zone/date/time-slot, so intra-shift granularity is available to the planning engine.
- As a labor planning PM, I want confirmed orders to arrive within 15 minutes of being placed in the OMS, so actual-demand requirements stay current.
- As an ops analyst, I want stale forecasts (>2h old) flagged, so I know when requirement calculations are running on outdated signals.

## 4. Data Model Impact

Entities: `DEMAND_FORECAST`, `ORDER`, `ORDER_LINE` (ERD reference §2.9–2.11). No new entities/fields proposed. No ERD version bump required.

## 5. API / Interface Design

- `POST /forecasts` (batch-friendly, JSON payload close to OMS/statistical-model export shape)
- `POST /orders` with nested `order_lines[]` (JSON/IDOC-style per [CLAUDE.md](../../CLAUDE.md) §2)
- `GET /forecasts?warehouse_id=&zone_id=&date=` and equivalent for orders
- Internal freshness-check job feeding the Forecast Freshness observability check (ERD reference §7)

## 6. Acceptance Criteria

- Given a forecast record older than 2 hours for an active warehouse-zone pair, when the freshness check runs, then an alert is raised to Demand Planning within 15 minutes.
- Given an order with `status = received` and no `expected_ship_date`, when saved, then the write is rejected.
- Given an `ORDER_LINE.quantity <= 0`, when saved, then the write is rejected.
- Given a duplicate `order_id`, when ingested, then the record is rejected/upserted per defined dedup rule (not silently duplicated).

## 7. Test Cases

See [testcases/03-demand-signal-ingestion.md](../testcases/03-demand-signal-ingestion.md).

## 8. Open Questions

- Exact upsert vs. reject behavior for duplicate order ingestion from a replaying feed.
- Which OMS/WMS feed format is the first integration target (Manhattan/Blue Yonder export shape assumed per Initiative Objectives — confirm before building the adapter).

## 9. Approval

- [ ] Reviewed by product owner
- [ ] Approved to start development — approval recorded here and in [DECISION_LOG.md](../DECISION_LOG.md)
