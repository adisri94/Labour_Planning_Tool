-- Warehouse Labor Planning Tool -- Local mock data source (SQLite)
-- Sprint 1 (BL-1): Facility & Org Master Data
-- Mirrors docs/reference/labor-planning-erd-reference-v2.md sections 2.1-2.5.
-- This file is extended by later sprints as new entities are introduced.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS warehouse (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS zone (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    zone_type TEXT NOT NULL CHECK (zone_type IN ('receiving','putaway','picking','sorting','packing','shipping')),
    capacity INTEGER
);

CREATE TABLE IF NOT EXISTS job_role (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    skill_level TEXT CHECK (skill_level IN ('entry','intermediate','senior')),
    labor_rate REAL NOT NULL CHECK (labor_rate > 0)
);

CREATE TABLE IF NOT EXISTS employee (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    employee_type TEXT NOT NULL CHECK (employee_type IN ('full_time','part_time','temporary')),
    employment_status TEXT NOT NULL CHECK (employment_status IN ('active','on_leave','terminated')),
    hire_date TEXT
);

CREATE TABLE IF NOT EXISTS employee_role (
    employee_id TEXT NOT NULL REFERENCES employee(id),
    job_role_id TEXT NOT NULL REFERENCES job_role(id),
    certified_date TEXT,
    is_primary INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (employee_id, job_role_id)
);

CREATE INDEX IF NOT EXISTS idx_zone_warehouse ON zone(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_employee_warehouse ON employee(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_employee_role_employee ON employee_role(employee_id);

-- Sprint 2 (BL-2): Shift & Compliance Configuration
-- Mirrors docs/reference/labor-planning-erd-reference-v2.md sections 2.6-2.8, PLUS
-- is_active/activated_by/activated_at -- proposed additions (ERD v3, see
-- docs/features/02-shift-compliance-configuration.md Section 4.1) standing in for
-- the "legal sign-off" gate.

CREATE TABLE IF NOT EXISTS shift_template (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL REFERENCES warehouse(id),
    name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    shift_type TEXT NOT NULL CHECK (shift_type IN ('day','afternoon','night')),
    days_of_week INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 0,
    activated_by TEXT,
    activated_at TEXT
);

CREATE TABLE IF NOT EXISTS labor_regulation (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    max_hours_per_day INTEGER NOT NULL CHECK (max_hours_per_day > 0),
    max_hours_per_week INTEGER NOT NULL CHECK (max_hours_per_week > 0),
    break_interval_mins INTEGER,
    overtime_multiplier REAL,
    region TEXT,
    is_active INTEGER NOT NULL DEFAULT 0,
    activated_by TEXT,
    activated_at TEXT
);

CREATE TABLE IF NOT EXISTS regulation_shift (
    regulation_id TEXT NOT NULL REFERENCES labor_regulation(id),
    shift_template_id TEXT NOT NULL REFERENCES shift_template(id),
    PRIMARY KEY (regulation_id, shift_template_id)
);

CREATE INDEX IF NOT EXISTS idx_shift_template_warehouse ON shift_template(warehouse_id);
