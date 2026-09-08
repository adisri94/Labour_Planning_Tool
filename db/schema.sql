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
