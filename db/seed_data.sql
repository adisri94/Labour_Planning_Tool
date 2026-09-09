-- Warehouse Labor Planning Tool -- Demo seed data (Sprint 1 / BL-1)
-- Sized to support the ERD reference §4 worked example once later sprints land:
-- Pick Zone A + Unit Pick task type + 480-min shift -> 1 required picker.
-- Localized to a US warehouse/workforce (see docs/DECISION_LOG.md, 2026-09-10).

INSERT INTO warehouse (id, name, location, timezone) VALUES
    ('wh-001', 'Chicago FC-1', 'Chicago, IL, USA', 'America/Chicago');

INSERT INTO zone (id, warehouse_id, name, zone_type, capacity) VALUES
    ('zone-001', 'wh-001', 'Pick Zone A', 'picking', 15),
    ('zone-002', 'wh-001', 'Pack Zone A', 'packing', 10),
    ('zone-003', 'wh-001', 'Receiving Dock', 'receiving', 8),
    ('zone-004', 'wh-001', 'Outbound Shipping', 'shipping', 8);

INSERT INTO job_role (id, name, skill_level, labor_rate) VALUES
    ('role-picker', 'Picker', 'entry', 19.50),
    ('role-packer', 'Packer', 'entry', 19.00),
    ('role-forklift', 'Forklift Operator', 'intermediate', 24.00),
    ('role-receiver', 'Receiver', 'entry', 18.50);

INSERT INTO employee (id, warehouse_id, name, employee_type, employment_status, hire_date) VALUES
    ('emp-001', 'wh-001', 'Emily Carter',    'full_time', 'active',     '2024-01-15'),
    ('emp-002', 'wh-001', 'Michael Johnson', 'full_time', 'active',     '2024-02-01'),
    ('emp-003', 'wh-001', 'Sarah Williams',  'full_time', 'active',     '2024-03-10'),
    ('emp-004', 'wh-001', 'David Brown',     'part_time', 'active',     '2024-04-05'),
    ('emp-005', 'wh-001', 'Jessica Davis',   'full_time', 'active',     '2024-05-20'),
    ('emp-006', 'wh-001', 'James Miller',    'full_time', 'active',     '2024-06-11'),
    ('emp-007', 'wh-001', 'Ashley Wilson',   'temporary', 'active',     '2024-07-01'),
    ('emp-008', 'wh-001', 'Christopher Lee', 'full_time', 'on_leave',   '2023-11-19'),
    ('emp-009', 'wh-001', 'Amanda Martinez', 'full_time', 'active',     '2024-08-14'),
    ('emp-010', 'wh-001', 'Daniel Anderson', 'full_time', 'terminated', '2023-05-02'),
    ('emp-011', 'wh-001', 'Olivia Taylor',   'part_time', 'active',     '2024-09-09'),
    ('emp-012', 'wh-001', 'Matthew Thomas',  'full_time', 'active',     '2024-01-29');

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
-- Three-shift pattern (Morning/Evening/Night) folded in from a manual
-- DB Browser edit -- see docs/DECISION_LOG.md, 2026-09-10.
INSERT INTO shift_template (id, warehouse_id, name, start_time, end_time, shift_type, days_of_week, is_active, activated_by, activated_at) VALUES
    ('shift-morning', 'wh-001', 'Morning Shift', '06:00', '14:00', 'day',      62, 1, 'Labor Planning PM', '2026-09-09T09:00:00'),
    ('shift-evening', 'wh-001', 'Evening Shift', '14:00', '22:00', 'afternoon', 62, 1, 'Labor Planning PM', '2026-09-10T09:00:00'),
    ('shift-night',   'wh-001', 'Night Shift',   '22:00', '06:00', 'night',    62, 1, 'Labor Planning PM', '2026-09-09T09:00:00');

-- break_interval_mins kept at 60 (mandatory meal break); each shift is now
-- 8 hours gross (480 min), so available_shift_minutes = 420 for all three
-- -- this no longer matches the ERD reference §4 worked example's 540/480
-- figures (that example used a 9-hour shift), which is an accepted,
-- documented deviation now that the demo uses a real 3-shift 8hr pattern.
-- FLSA's own overtime threshold is 40 hrs/week (8 hrs/day used here as the
-- per-shift cap), and 1.5x is the actual FLSA overtime multiplier.
INSERT INTO labor_regulation (id, name, max_hours_per_day, max_hours_per_week, break_interval_mins, overtime_multiplier, region, is_active, activated_by, activated_at) VALUES
    ('reg-flsa', 'Fair Labor Standards Act (FLSA)', 8, 40, 60, 1.5, 'USA', 1, 'Legal & Compliance', '2026-09-09T09:00:00');

INSERT INTO regulation_shift (regulation_id, shift_template_id) VALUES
    ('reg-flsa', 'shift-morning'),
    ('reg-flsa', 'shift-evening'),
    ('reg-flsa', 'shift-night');
