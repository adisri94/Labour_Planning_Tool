# Warehouse Labor Planning Tool | ERD Reference

**Entity Relationship Diagram — Data Model Reference Document**
**Version 3**

---

## 1. Overview

This document describes the data model underpinning the Warehouse Labor Planning Tool — a system designed to translate demand signals and actual order data into granular, actionable labor requirements that warehouse managers can use to plan staffing for upcoming shifts.

The model is structured across three logical layers:

- **Input layer** — Captures the raw signals that drive labor demand: warehouses, zones, employees, job roles, shifts, labor regulations, demand forecasts, orders, and order lines.
- **Task layer** — Defines and instantiates the atomic units of work (task types and tasks) performed within each zone, providing the bridge between demand signals and labor calculations.
- **Output layer** — Produces labor requirements and labor plans by aggregating task minutes and matching them to available employee shifts.

The core labor calculation is:

```
required_headcount  =  Σ (task.quantity × task_type.std_time_mins)  ÷  available_shift_minutes
```

This document covers each entity in detail, listing all attributes with their types and descriptions, followed by a full relationship catalogue.

---

## 2. Entities

### Input Layer — Facility & Organisation

---

#### 2.1 WAREHOUSE

The top-level entity representing a physical fulfillment or distribution facility. Every other entity in the model is either directly or indirectly scoped to a warehouse. It acts as the root namespace for zones, employees, shifts, demand forecasts, and orders, ensuring that data from one facility never bleeds into planning for another.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the warehouse. |
| `name` | String | | Human-readable name of the facility (e.g., Mumbai FC-1). |
| `location` | String | | Physical address or city/region identifier. |
| `timezone` | String | | IANA timezone string (e.g., Asia/Kolkata) used to correctly interpret shift times and forecast windows. |

---

#### 2.2 ZONE

A named operational area within a warehouse where specific types of work are performed. Zones provide the granularity necessary for labor planning — demand, tasks, and labor requirements are all computed at zone level, not at the warehouse level as a whole. Typical zones include Inbound Receiving, Putaway, Picking, Sorting, Packing, and Outbound Shipping.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the zone. |
| `warehouse_id` | UUID | FK | References the WAREHOUSE this zone belongs to. |
| `name` | String | | Display name of the zone (e.g., Pick Zone A). |
| `zone_type` | String | | Functional classification: `receiving`, `putaway`, `picking`, `sorting`, `packing`, `shipping`. |
| `capacity` | Integer | | Maximum concurrent headcount this zone can physically accommodate. |

---

#### 2.3 EMPLOYEE

Represents an individual worker who can be assigned to shifts within a warehouse. The employee record captures identity and employment classification data. Skill qualifications are held separately in EMPLOYEE_ROLE, allowing a single worker to be certified in multiple job roles across zones.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the employee. |
| `warehouse_id` | UUID | FK | References the WAREHOUSE this employee is primarily assigned to. |
| `name` | String | | Full name of the employee. |
| `employee_type` | String | | Classification: `full_time`, `part_time`, or `temporary`. |
| `employment_status` | String | | Current status: `active`, `on_leave`, `terminated`. |
| `hire_date` | Date | | Date the employee joined, used for tenure-based regulation checks. |

---

#### 2.4 JOB_ROLE

Defines a category of work that requires a specific skill set. Job roles are referenced both by TASK_TYPE (to indicate which role is needed to execute a task) and by LABOR_REQUIREMENT (to specify the type of labor being requested). Linking these through a shared entity ensures that the system can match the right employees to the right requirements automatically.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the job role. |
| `name` | String | | Role name (e.g., Picker, Packer, Forklift Operator, Sorter, Receiver). |
| `skill_level` | String | | Relative skill tier: `entry`, `intermediate`, or `senior`. |
| `labor_rate` | Float | | Hourly cost rate for this role, used in workforce cost planning. |

---

#### 2.5 EMPLOYEE_ROLE

A bridge (junction) entity that records which job roles an employee is qualified to perform. This many-to-many relationship enables cross-training — a single employee can be certified in multiple roles, giving the planning engine flexibility to fill gaps across zones. The `is_primary` flag identifies the employee's default role when no shortage situation requires otherwise.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `employee_id` | UUID | FK | References the EMPLOYEE. |
| `job_role_id` | UUID | FK | References the JOB_ROLE the employee is qualified for. |
| `certified_date` | Date | | Date the certification or training was completed. |
| `is_primary` | Boolean | | True if this is the employee's primary role; false for secondary cross-trained roles. |

---

#### 2.6 SHIFT_TEMPLATE

Defines a reusable shift schedule pattern for a warehouse. Templates capture the standard operating hours and the days of the week they apply. They are used as the time dimension when computing labor requirements — a requirement is always expressed within the context of a specific shift. Templates are also linked to regulations, allowing the system to enforce compliance rules per shift type.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the shift template. |
| `warehouse_id` | UUID | FK | References the WAREHOUSE that operates this shift. |
| `name` | String | | Descriptive name (e.g., Morning Shift, Night Shift). |
| `start_time` | Time | | Scheduled shift start time in the warehouse's local timezone. |
| `end_time` | Time | | Scheduled shift end time. |
| `shift_type` | String | | Classification: `day`, `afternoon`, or `night`. |
| `days_of_week` | Integer | | Bitmask representing active days (e.g., 62 = Mon–Fri). |
| `is_active` | Boolean | | *(Added v3)* Whether this template has passed the Shift & Compliance activation gate (Section 5.2) and may be attached to/used by other features. Defaults to `false` on creation. |
| `activated_by` | String | | *(Added v3)* Who activated this record in-app. Expected to correspond to a real legal sign-off recorded by process convention (not automated) in the project's Decision Log. |
| `activated_at` | Timestamp | | *(Added v3)* When this record was activated. |

---

#### 2.7 LABOR_REGULATION

Captures the legal and contractual constraints that govern how employees can be scheduled. Multiple regulations can apply to the same shift (e.g., a national labor law plus a union agreement), which is why the relationship is managed through the REGULATION_SHIFT bridge table. The planning engine applies these constraints when constructing LABOR_PLAN records to ensure compliance.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the regulation. |
| `name` | String | | Name or reference number of the regulation (e.g., Factories Act 1948, Union CBA v3). |
| `max_hours_per_day` | Integer | | Maximum hours an employee may work in a single day under this regulation. |
| `max_hours_per_week` | Integer | | Maximum hours per rolling seven-day period. |
| `break_interval_mins` | Integer | | Mandatory break after this many continuous working minutes. |
| `overtime_multiplier` | Float | | Pay multiplier for hours beyond the standard threshold (e.g., 1.5 for time-and-a-half). |
| `region` | String | | Jurisdiction or region where this regulation applies. |
| `is_active` | Boolean | | *(Added v3)* Whether this regulation has passed the activation gate and may be attached to a shift template. Defaults to `false` on creation. |
| `activated_by` | String | | *(Added v3)* Who activated this record in-app. |
| `activated_at` | Timestamp | | *(Added v3)* When this record was activated. |

---

#### 2.8 REGULATION_SHIFT

A bridge entity linking labor regulations to the shift templates they govern. The many-to-many design allows multiple overlapping regulations (national law, state law, union agreement) to simultaneously constrain the same shift, and a single regulation to apply across multiple shift types.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `regulation_id` | UUID | FK | References the LABOR_REGULATION being applied. |
| `shift_template_id` | UUID | FK | References the SHIFT_TEMPLATE being governed. |

---

### Input Layer — Demand Signals

---

#### 2.9 DEMAND_FORECAST

Stores forward-looking demand signals ingested from external systems such as order management platforms, WMS integrations, or statistical forecasting engines. Forecasts are scoped to a specific warehouse, zone, date, and time slot — enabling sub-shift granularity in labor planning. Each record carries a confidence score so the planning engine can weight forecast-driven requirements appropriately against actuals.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the forecast record. |
| `warehouse_id` | UUID | FK | References the WAREHOUSE receiving the forecasted demand. |
| `zone_id` | UUID | FK | The specific ZONE the forecasted volume applies to. |
| `forecast_date` | Date | | Calendar date for which the forecast is valid. |
| `time_slot` | String | | Sub-shift time window (e.g., `06:00–07:00`) for intra-shift granularity. |
| `forecast_volume` | Float | | Predicted workload volume for this zone, date, and time slot. |
| `unit_type` | String | | The unit being forecasted: `units`, `cases`, `pallets`, or `orders`. |
| `signal_source` | String | | System or model that generated the signal (e.g., `OMS_feed`, `statistical_model`). |
| `confidence_score` | Float | | A 0–1 score indicating forecast reliability, used to weight requirement calculations. |

---

#### 2.10 ORDER

Represents an actual customer or transfer order received by the warehouse. Unlike a demand forecast, an order is a confirmed commitment with a specific ship date and priority. Orders serve as the parent record for ORDER_LINE items, and the task chain that drives actual labor requirements flows from those line items downward.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the order. |
| `warehouse_id` | UUID | FK | References the WAREHOUSE that will fulfill this order. |
| `received_at` | Timestamp | | Exact date and time the order was received into the system. |
| `expected_ship_date` | Date | | The date by which the order must be dispatched, driving scheduling urgency. |
| `priority` | String | | Fulfillment priority: `standard`, `expedited`, or `critical`. |
| `status` | String | | Current lifecycle state: `received`, `in_progress`, `fulfilled`, or `cancelled`. |

---

#### 2.11 ORDER_LINE

A single line item within an order, representing a specific SKU and quantity that needs to be processed. Each order line is tied to a zone because different SKUs may be stored in different areas of the warehouse, and the zone association determines which task types will be generated from this line. One order line can generate multiple tasks of different types (pick, sort, pack) across different zones.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the order line. |
| `order_id` | UUID | FK | References the parent ORDER. |
| `zone_id` | UUID | FK | The ZONE where this item is stored or where primary processing begins. |
| `sku` | String | | Stock Keeping Unit identifier for the product. |
| `quantity` | Integer | | Number of units to be picked or processed for this line. |
| `pick_type` | String | | Method of picking: `unit_pick`, `case_pick`, or `pallet_pick` — affects which task type applies. |

---

### Task Layer — Units of Work

---

#### 2.12 TASK_TYPE

Defines a category of repeatable work performed within a specific zone, along with the engineering standard time required to complete one unit of that work. This is the most critical configuration entity in the model — the `std_time_mins` value is the multiplier that converts task volume into labour minutes, making it the direct input to the headcount calculation. Each task type is also associated with a job role, so the system knows which skill type is required to execute it.

**Example task types by zone:**

- Picking zone: Unit Pick (`std_time`: 0.5 mins/unit), Case Pick (`std_time`: 1.2 mins/case)
- Packing zone: Pack & Label (`std_time`: 2.0 mins/unit)
- Receiving zone: Inbound Scan & Putaway (`std_time`: 3.5 mins/pallet)

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the task type. |
| `zone_id` | UUID | FK | The ZONE in which this task type is performed. |
| `required_role_id` | UUID | FK | References the JOB_ROLE required to perform this task type. |
| `name` | String | | Descriptive name (e.g., Unit Pick, Pallet Putaway, Pack & Label). |
| `std_time_mins` | Float | | Engineered standard time in minutes to complete one unit of this task. Core input to the headcount formula. |
| `unit_of_measure` | String | | The unit the `std_time` applies to: `unit`, `case`, `pallet`, or `order`. |
| `description` | String | | Free-text description of the task, including any special conditions or exceptions. |

---

#### 2.13 TASK

The atomic, instantiated unit of work to be performed. Tasks are generated from one of two sources: ORDER_LINE (for confirmed orders) or DEMAND_FORECAST (for projected workload). The `source_type` field distinguishes these cases. Multiple tasks of different types can be generated from a single order line as it moves through different zones. Tasks roll up to LABOR_REQUIREMENT through the headcount calculation engine.

The calculation flow from tasks to requirements is:

```
total_task_minutes (per zone + role + shift + slot)  =  Σ (task.quantity × task_type.std_time_mins)
```

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the task instance. |
| `task_type_id` | UUID | FK | References the TASK_TYPE defining how this task is performed and its standard time. |
| `zone_id` | UUID | FK | The ZONE where this task is to be executed. |
| `order_line_id` | UUID | FK | References the ORDER_LINE that generated this task. Null for forecast-driven tasks. |
| `forecast_id` | UUID | FK | References the DEMAND_FORECAST that projected this task. Null for actual-order tasks. |
| `source_type` | String | | Indicates origin: `actual` (from order) or `forecast` (from demand signal). |
| `quantity` | Integer | | Number of units to be processed for this task instance. |
| `scheduled_date` | Date | | The date on which this task is expected to be executed. |
| `time_slot` | String | | Sub-shift time window this task is expected to fall within. |
| `status` | String | | Lifecycle state: `pending`, `in_progress`, `completed`, or `cancelled`. |

---

### Output Layer — Requirements & Planning

---

#### 2.14 LABOR_REQUIREMENT

The central output entity of the planning engine. Each record represents the computed headcount needed for a specific combination of zone, job role, shift, date, and time slot. It is derived by aggregating all task minutes within that combination and dividing by the available working minutes in the shift (net of breaks). Labor requirements provide the input to LABOR_PLAN, where the manager assigns actual employees.

Headcount formula applied per record:

```
required_headcount  =  CEIL( total_task_minutes  ÷  available_shift_minutes )
```

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the labor requirement record. |
| `zone_id` | UUID | FK | The ZONE this requirement applies to. |
| `job_role_id` | UUID | FK | The JOB_ROLE (skill type) being requested. |
| `shift_template_id` | UUID | FK | The SHIFT_TEMPLATE defining the time window. |
| `req_date` | Date | | The calendar date this requirement is for. |
| `time_slot` | String | | Sub-shift bucket for granular intra-shift planning. |
| `total_task_minutes` | Float | | Aggregated labour minutes derived from all tasks in scope. Input to headcount formula. |
| `required_headcount` | Integer | | Computed number of workers needed. Always rounded up (ceiling). |
| `source_type` | String | | Whether driven by `forecast`, `actual` orders, or a `blended` combination of both. |
| `status` | String | | Planning state: `draft`, `confirmed`, or `locked`. |

---

#### 2.15 EMPLOYEE_SHIFT

Records the scheduled or actual assignment of an employee to a specific shift on a specific date. This entity represents the supply side of the labor equation — it is what is available to be matched against LABOR_REQUIREMENT records. Actual start and end times allow post-shift variance analysis between planned and actual availability.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the employee shift record. |
| `employee_id` | UUID | FK | References the EMPLOYEE being scheduled. |
| `shift_template_id` | UUID | FK | References the SHIFT_TEMPLATE the employee is assigned to. |
| `shift_date` | Date | | The date of this shift occurrence. |
| `status` | String | | Scheduling state: `scheduled`, `confirmed`, `completed`, or `absent`. |
| `actual_start` | Time | | Recorded actual start time, populated post-shift for attendance tracking. |
| `actual_end` | Time | | Recorded actual end time. |

---

#### 2.16 LABOR_PLAN

The final planning output that links a labor requirement to a specific employee shift, completing the demand-to-supply matching loop. Each record indicates how many workers from a given employee shift are being allocated to fulfil a given requirement. Multiple plan records can fulfil a single requirement (partial allocations from different shifts or employees), and a single employee shift can contribute to multiple requirements.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `id` | UUID | PK | Unique identifier for the plan record. |
| `labor_requirement_id` | UUID | FK | References the LABOR_REQUIREMENT being fulfilled. |
| `employee_shift_id` | UUID | FK | References the EMPLOYEE_SHIFT providing the labour supply. |
| `planned_headcount` | Integer | | Number of workers from this shift being allocated to this requirement. |
| `plan_status` | String | | Status: `draft`, `confirmed`, or `executed`. |
| `created_at` | Timestamp | | When this plan record was created, supporting audit and version history. |

---

## 3. Relationships

The table below catalogues every relationship in the model, including cardinality and a plain-language description of the business rule it encodes.

| From Entity | Cardinality | To Entity | Description |
|-------------|-------------|-----------|-------------|
| WAREHOUSE | 1 to many | ZONE | A warehouse contains one or more operational zones. Every zone belongs to exactly one warehouse. |
| WAREHOUSE | 1 to many | EMPLOYEE | A warehouse employs one or more employees. Each employee is primarily based at one warehouse. |
| WAREHOUSE | 1 to many | SHIFT_TEMPLATE | A warehouse defines one or more shift patterns. Shift templates are warehouse-specific. |
| WAREHOUSE | 1 to many | DEMAND_FORECAST | Demand forecasts are received at warehouse level and further scoped to a zone. |
| WAREHOUSE | 1 to many | ORDER | Actual orders are fulfilled by a specific warehouse. |
| ZONE | 1 to many | TASK_TYPE | Each zone defines the types of tasks performed within it. A task type belongs to exactly one zone. |
| ZONE | 1 to many | TASK | Tasks are executed within a specific zone. The zone determines which task types are applicable. |
| ZONE | 1 to many | ORDER_LINE | An order line is associated with the zone where the item is stored or primarily processed. |
| ZONE | 1 to many | DEMAND_FORECAST | Forecast signals are scoped to a zone, providing the granularity needed for per-zone labor planning. |
| ZONE | 1 to many | LABOR_REQUIREMENT | Labor requirements are computed at zone level. Each requirement belongs to one zone. |
| JOB_ROLE | 1 to many | TASK_TYPE | Each task type requires a specific job role. The role determines which employees are eligible to perform it. |
| JOB_ROLE | 1 to many | EMPLOYEE_ROLE | A job role can be held by many employees through their employee-role certification records. |
| JOB_ROLE | 1 to many | LABOR_REQUIREMENT | Labor requirements specify the role type being requested, enabling employee matching. |
| EMPLOYEE | 1 to many | EMPLOYEE_ROLE | An employee can hold multiple role qualifications, enabling cross-training and flexible scheduling. |
| EMPLOYEE | 1 to many | EMPLOYEE_SHIFT | An employee is scheduled across many shift instances over time. |
| TASK_TYPE | 1 to many | TASK | A task type categorises many individual task instances. The `std_time_mins` on the type is applied to every instance. |
| SHIFT_TEMPLATE | 1 to many | EMPLOYEE_SHIFT | A shift template is instantiated into many employee shift records, one per employee per date. |
| SHIFT_TEMPLATE | 1 to many | LABOR_REQUIREMENT | Requirements are expressed within the time window of a shift template. |
| SHIFT_TEMPLATE | 1 to many | REGULATION_SHIFT | A shift can be governed by multiple regulations through the bridge table. |
| LABOR_REGULATION | 1 to many | REGULATION_SHIFT | A regulation can apply to multiple shift templates through the bridge table. |
| ORDER | 1 to many | ORDER_LINE | An order contains one or more line items, each representing a distinct SKU and quantity. |
| ORDER_LINE | 1 to many | TASK | Each order line generates one or more tasks as it moves through the warehouse zones. |
| ORDER | 1 to many | LABOR_REQUIREMENT | Orders drive labor requirements indirectly via the task chain. The direct link provides traceability back to the source order. |
| DEMAND_FORECAST | 1 to many | TASK | Forecast records generate projected tasks, enabling labor planning before actual orders are received. |
| DEMAND_FORECAST | 1 to many | LABOR_REQUIREMENT | Forecasts drive requirements directly when no actual order exists yet, allowing advance planning. |
| TASK | 1 to many | LABOR_REQUIREMENT | Tasks aggregate into labor requirements. The engine sums task minutes per zone + role + shift + slot to compute headcount. |
| LABOR_REQUIREMENT | 1 to many | LABOR_PLAN | A labor requirement can be fulfilled by multiple plan records (partial allocations from different shifts). |
| EMPLOYEE_SHIFT | 1 to many | LABOR_PLAN | An employee shift can contribute headcount to multiple requirements across different zones or time slots. |

---

## 4. Labor Calculation Walkthrough

The following example illustrates how the model translates a received order into a labor requirement for the picking zone.

### 4.1 Example Scenario

- An ORDER is received with 3 ORDER_LINE records totalling 600 units to be picked from Pick Zone A.
- The applicable TASK_TYPE for Pick Zone A is **Unit Pick** with a `std_time_mins` of 0.5 minutes per unit.
- The SHIFT_TEMPLATE is a 9-hour shift with a 60-minute break, giving **480 available working minutes**.

### 4.2 Calculation Steps

**Step 1 — Generate tasks:**

```
600 units across 3 order lines  →  3 TASK records (one per line), each with source_type = actual
```

**Step 2 — Sum task minutes:**

```
total_task_minutes  =  600 units × 0.5 mins/unit  =  300 minutes
```

**Step 3 — Compute headcount:**

```
required_headcount  =  CEIL( 300 ÷ 480 )  =  CEIL( 0.625 )  =  1 worker
```

**Step 4 — Create LABOR_PLAN:**

The planning engine searches EMPLOYEE_SHIFT records for employees qualified as Pickers (via EMPLOYEE_ROLE) who are scheduled during the relevant shift. It creates a LABOR_PLAN record assigning 1 picker from an available EMPLOYEE_SHIFT to fulfil the requirement.

### 4.3 Forecast-Driven Planning

When no actual orders exist yet, the same calculation runs using DEMAND_FORECAST records as the source. The engine generates TASK records with `source_type = forecast`, which flow through the same aggregation logic to produce LABOR_REQUIREMENT records. As actual orders arrive and replace forecast tasks, the requirements update automatically — giving managers a continuously improving view of upcoming staffing needs.

---

## 5. Data Product Definitions

This section formalises the three logical layers of the data model as independently owned, discoverable, and trustworthy Data Products. Each data product is defined with its owner, consumers, quality contracts (SLAs), governance rules, and observability requirements — the properties that elevate a data model from a backend schema into a product that teams can rely on.

### 5.1 Workforce Master Data Product

The authoritative source of truth for all workforce-related reference data. Consumed by the planning engine and any downstream system that needs to know who works where, in what role, and under what classification.

| Property | Detail |
|----------|--------|
| **Entities** | WAREHOUSE, ZONE, EMPLOYEE, JOB_ROLE, EMPLOYEE_ROLE |
| **Owner** | HR / Workforce Operations team |
| **Consumers** | Labor Planning Engine, Payroll system, HR dashboards, Compliance audit reports |
| **Refresh SLA** | Propagated within 1 hour of any HR system change. `EMPLOYEE.employment_status` must reflect terminations within 30 minutes. |
| **Quality Contracts** | `EMPLOYEE.id`, `name`, `employee_type` must never be null. `EMPLOYEE_ROLE` must have at least one record per active employee. `JOB_ROLE.labor_rate` must be > 0. |

### 5.2 Shift and Compliance Data Product

Manages all configuration and regulatory constraints that govern how employees can be scheduled. Any change to this product propagates immediately to the planning engine and must follow the governance process described in Section 6.

| Property | Detail |
|----------|--------|
| **Entities** | SHIFT_TEMPLATE, LABOR_REGULATION, REGULATION_SHIFT |
| **Owner** | Operations / Legal and Compliance team |
| **Quality Contracts** | `SHIFT_TEMPLATE.start_time` and `end_time` must not be null. `LABOR_REGULATION.max_hours_per_day` and `max_hours_per_week` must be > 0. Changes require Legal sign-off before activation, enforced in-app *(added v3)* via the `is_active`/`activated_by`/`activated_at` gate on both entities: a `SHIFT_TEMPLATE` or `LABOR_REGULATION` is created `is_active = false` and cannot be attached to/used by other features (e.g., `REGULATION_SHIFT`) until explicitly activated. The gate enforces that activation happened; the actual legal sign-off evidence is a process convention recorded in the project's Decision Log, not something this schema automates. |

### 5.3 Demand Signals Data Product

The real-time ingestion layer for both confirmed orders and forward-looking forecast signals. The freshness and confidence of this product directly determines the accuracy of all labor requirements generated downstream.

| Property | Detail |
|----------|--------|
| **Entities** | DEMAND_FORECAST, ORDER, ORDER_LINE |
| **Refresh SLA** | `DEMAND_FORECAST`: stale if older than 2 hours. New ORDER records must be available within 15 minutes of receipt from the OMS. `DEMAND_FORECAST.confidence_score` must remain in the range 0.0 to 1.0. |
| **Quality Contracts** | `ORDER.expected_ship_date` must not be null on any record with `status = received` or `in_progress`. `ORDER_LINE.quantity` must be > 0. No duplicate `order_id` values. |

### 5.4 Labor Plan Data Product (Primary Output)

The final, consumer-facing output of the planning system. This is what warehouse managers read, act on, and are held accountable to. It has the highest SLA in the system — a late or incorrect labor plan directly causes overstaffing cost or operational failure.

| Property | Detail |
|----------|--------|
| **Entities** | LABOR_REQUIREMENT, EMPLOYEE_SHIFT, LABOR_PLAN |
| **Owner** | Labor Planning Product Manager |
| **Consumers** | Warehouse managers, Finance (cost reporting), Ops analytics dashboards, ML demand forecasting models |
| **Refresh SLA** | `LABOR_REQUIREMENT` must reach `status = confirmed` at least 12 hours before shift start. `LABOR_PLAN` must reach `plan_status = confirmed` before shift start. `EMPLOYEE_SHIFT.actual_start` and `actual_end` must be populated within 30 minutes of shift completion. |
| **Quality Contracts** | `LABOR_REQUIREMENT.required_headcount` must always be >= 1. `LABOR_PLAN.planned_headcount` sum per requirement must equal `required_headcount`. Variance between planned and actual headcount to be logged in `EMPLOYEE_SHIFT` post-shift. |

---

## 6. Governance and Change Management

Governance defines how changes to the data model are approved, communicated, and versioned. Without it, a schema change by one team silently breaks a dashboard or pipeline owned by another team.

### 6.1 Critical Field: `TASK_TYPE.std_time_mins`

The `std_time_mins` field on TASK_TYPE is the single most consequential value in the data model. It is the direct multiplier in the headcount formula: a change of 0.1 minutes per unit on a high-volume task type can shift the required headcount by one or more workers per shift across an entire facility. For this reason, it is treated as a versioned, governed field with the following rules:

- Every change to `std_time_mins` must be approved by the Industrial Engineering owner and the Labor Planning PM before it is written to the production database.
- A `change_log` table (`task_type_id`, `old_value`, `new_value`, `changed_by`, `changed_at`, `approved_by`) must record every update to this field with a full audit trail.
- A change triggers an automatic re-computation of all LABOR_REQUIREMENT records for the next 14 days for the affected zone. Warehouse managers are notified of any resulting headcount changes within 30 minutes.
- The field must never be null or zero. A DB-level constraint enforces `std_time_mins > 0` for all active task types.

### 6.2 Schema Change Protocol

Any structural change to an entity — adding a column, renaming a field, changing a data type, or deprecating a relationship — must follow the protocol below. This prevents silent downstream breakage, which is the most common failure mode of unmanaged data products.

- Notify all registered consumers at least 5 business days before a breaking change takes effect.
- Maintain backward compatibility for at least one full shift cycle (24 hours) after any non-breaking addition, to give automated consumers time to adapt.
- Increment the document version number in the header and add a changelog entry (date, author, change description) at the end of this document on every approved schema update.

---

## 7. Observability and Data Health Monitoring

Observability means the system can tell you, without manual investigation, whether each data product is healthy right now. The following automated checks should run continuously in the pipeline and alert the owning team within 15 minutes of any breach.

| Check | What It Monitors | Alert Owner |
|-------|-----------------|-------------|
| Forecast freshness check | No DEMAND_FORECAST record newer than 2 hours for any active warehouse-zone pair | Demand Planning team |
| Null headcount check | Any `LABOR_REQUIREMENT.required_headcount` that is null or zero for an upcoming shift | Labor Planning PM |
| Unconfirmed plan check | Any LABOR_PLAN still in `draft` status within 14 hours of its scheduled shift start | Warehouse manager + Labor Planning PM |
| `std_time_mins` drift check | Any `TASK_TYPE.std_time_mins` changed without an approved `change_log` entry in the preceding 24 hours | Industrial Engineering + Labor Planning PM |
| Post-shift variance check | `EMPLOYEE_SHIFT.actual_start` or `actual_end` still null more than 30 minutes after shift `end_time` | Warehouse manager |

---

## 8. Data Catalog Entry Template

Discoverability requires that every data product has a catalog entry — a published, searchable description that any potential consumer can find. The template below should be completed for each of the four data products defined in Section 5 and published to the organisation's internal data catalog (e.g., Atlan, DataHub, dbt docs, or Confluence).

```
Data Product Name:     [e.g. Labor Plan Data Product]

Domain:                [Workforce / Demand / Output]

Owner (name + team):   [Name, Team]

Description:           [One paragraph. What is it, what decisions does it enable?]

Source entities:       [Comma-separated list of entity names]

Known consumers:       [List teams and systems that read this product]

Refresh frequency:     [e.g. Real-time / Hourly / Per-shift / On-change]

SLA:                   [Freshness guarantee + null rules + critical constraints]

Known caveats:         [Known gaps, edge cases, or temporarily relaxed rules]

Contact / Slack:       [Owner's contact and team channel for questions]
```

---

## 9. Document Changelog

Every schema change, governance decision, or SLA update must be recorded here. This log is the audit trail that allows any consumer to understand how the data product has evolved and whether they need to update their integration.

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2025-06-19 | Aditya Srivastava | Initial release of ERD reference document. Entity model, relationship catalogue, and calculation walkthrough. |
| 2.0 | 2025-06-19 | Aditya Srivastava | Added Data Product Definitions (Section 5), Governance and Change Management (Section 6), Observability (Section 7), and Data Catalog Entry Template (Section 8) to the initial entity model. This version was the document's baseline prior to formal changelog discipline being applied retroactively on 2026-09-09. |
| 3.0 | 2026-09-09 | Aditya Srivastava | Sprint 2 (BL-2, Shift & Compliance Configuration): added `is_active`, `activated_by`, `activated_at` to SHIFT_TEMPLATE (Section 2.6) and LABOR_REGULATION (Section 2.7), implementing the "Legal sign-off before activation" contract (Section 5.2) as an enforced in-app gate rather than an unenforced statement. Non-breaking additive columns (nullable/defaulted); no existing consumers of this local-demo schema, so the standard 5-business-day breaking-change notice did not apply. See [docs/features/02-shift-compliance-configuration.md](../features/02-shift-compliance-configuration.md) Section 4.1 and [docs/DECISION_LOG.md](../DECISION_LOG.md) (2026-09-09). |
