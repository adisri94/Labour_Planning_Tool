-- Warehouse Labor Planning Tool -- Demo seed data (Sprint 1 / BL-1)
-- Sized to support the ERD reference §4 worked example once later sprints land:
-- Pick Zone A + Unit Pick task type + 480-min shift -> 1 required picker.

INSERT INTO warehouse (id, name, location, timezone) VALUES
    ('wh-001', 'Mumbai FC-1', 'Mumbai, India', 'Asia/Kolkata');

INSERT INTO zone (id, warehouse_id, name, zone_type, capacity) VALUES
    ('zone-001', 'wh-001', 'Pick Zone A', 'picking', 15),
    ('zone-002', 'wh-001', 'Pack Zone A', 'packing', 10),
    ('zone-003', 'wh-001', 'Receiving Dock', 'receiving', 8),
    ('zone-004', 'wh-001', 'Outbound Shipping', 'shipping', 8);

INSERT INTO job_role (id, name, skill_level, labor_rate) VALUES
    ('role-picker', 'Picker', 'entry', 180.0),
    ('role-packer', 'Packer', 'entry', 180.0),
    ('role-forklift', 'Forklift Operator', 'intermediate', 240.0),
    ('role-receiver', 'Receiver', 'entry', 175.0);

INSERT INTO employee (id, warehouse_id, name, employee_type, employment_status, hire_date) VALUES
    ('emp-001', 'wh-001', 'Aditi Rao',      'full_time', 'active',     '2024-01-15'),
    ('emp-002', 'wh-001', 'Rohan Mehta',    'full_time', 'active',     '2024-02-01'),
    ('emp-003', 'wh-001', 'Priya Nair',     'full_time', 'active',     '2024-03-10'),
    ('emp-004', 'wh-001', 'Vikram Singh',   'part_time', 'active',     '2024-04-05'),
    ('emp-005', 'wh-001', 'Sneha Kulkarni', 'full_time', 'active',     '2024-05-20'),
    ('emp-006', 'wh-001', 'Arjun Desai',    'full_time', 'active',     '2024-06-11'),
    ('emp-007', 'wh-001', 'Kavya Iyer',     'temporary', 'active',     '2024-07-01'),
    ('emp-008', 'wh-001', 'Manish Gupta',   'full_time', 'on_leave',   '2023-11-19'),
    ('emp-009', 'wh-001', 'Divya Shah',     'full_time', 'active',     '2024-08-14'),
    ('emp-010', 'wh-001', 'Karan Malhotra', 'full_time', 'terminated', '2023-05-02'),
    ('emp-011', 'wh-001', 'Neha Joshi',     'part_time', 'active',     '2024-09-09'),
    ('emp-012', 'wh-001', 'Suresh Pillai',  'full_time', 'active',     '2024-01-29');

INSERT INTO employee_role (employee_id, job_role_id, certified_date, is_primary) VALUES
    ('emp-001', 'role-picker',   '2024-01-20', 1),
    ('emp-002', 'role-picker',   '2024-02-05', 1),
    ('emp-003', 'role-packer',   '2024-03-15', 1),
    ('emp-004', 'role-picker',   '2024-04-10', 1),
    ('emp-005', 'role-packer',   '2024-05-25', 1),
    ('emp-006', 'role-forklift', '2024-06-15', 1),
    ('emp-006', 'role-receiver', '2024-06-16', 0),
    ('emp-007', 'role-picker',   '2024-07-05', 1),
    ('emp-008', 'role-packer',   '2023-11-25', 1),
    ('emp-009', 'role-receiver', '2024-08-18', 1),
    ('emp-010', 'role-picker',   '2023-05-10', 1),
    ('emp-011', 'role-picker',   '2024-09-14', 1),
    ('emp-012', 'role-forklift', '2024-02-02', 1);

-- Sprint 2 (BL-2): pre-activated so Sprint 3+ demos aren't blocked by the
-- legal sign-off gate (see docs/features/02-shift-compliance-configuration.md).
INSERT INTO shift_template (id, warehouse_id, name, start_time, end_time, shift_type, days_of_week, is_active, activated_by, activated_at) VALUES
    ('shift-morning', 'wh-001', 'Morning Shift', '06:00', '15:00', 'day',   62, 1, 'Labor Planning PM', '2026-09-09T09:00:00'),
    ('shift-night',   'wh-001', 'Night Shift',   '22:00', '06:00', 'night', 62, 1, 'Labor Planning PM', '2026-09-09T09:00:00');

INSERT INTO labor_regulation (id, name, max_hours_per_day, max_hours_per_week, break_interval_mins, overtime_multiplier, region, is_active, activated_by, activated_at) VALUES
    ('reg-factories-act', 'Factories Act 1948', 9, 48, 60, 1.5, 'India', 1, 'Legal & Compliance', '2026-09-09T09:00:00');

INSERT INTO regulation_shift (regulation_id, shift_template_id) VALUES
    ('reg-factories-act', 'shift-morning'),
    ('reg-factories-act', 'shift-night');
