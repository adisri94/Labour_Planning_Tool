"""Automated tests for Sprint 1 (BL-1): Facility & Org Master Data.

Backfills docs/testcases/01-facility-org-master-data.md TC-1..TC-14 and
TC-18..TC-20 as runnable tests. TC-5 (frontend rendering) and
TC-15..TC-17 (db/init_db.py bootstrap script) are not FastAPI-client
testable -- TC-15..TC-17 are covered separately in test_init_db.py; TC-5
remains a manual/browser check per the test case doc.
"""


# ---- US-1: View zones and capacity within a warehouse ----------------------


def test_tc1_list_zones_for_warehouse_with_zones(client, warehouse):
    for zone_id, name, zone_type, capacity in [
        ("zone-001", "Pick Zone A", "picking", 15),
        ("zone-002", "Pack Zone A", "packing", 10),
        ("zone-003", "Receiving Dock", "receiving", 8),
    ]:
        res = client.post(
            f"/warehouses/{warehouse['id']}/zones",
            json={"id": zone_id, "name": name, "zone_type": zone_type, "capacity": capacity},
        )
        assert res.status_code == 201

    res = client.get(f"/warehouses/{warehouse['id']}/zones")
    assert res.status_code == 200
    zones = res.json()
    assert len(zones) == 3
    for z in zones:
        assert {"name", "zone_type", "capacity"} <= z.keys()


def test_tc2_list_zones_for_warehouse_with_none(client, warehouse):
    res = client.get(f"/warehouses/{warehouse['id']}/zones")
    assert res.status_code == 200
    assert res.json() == []


def test_tc3_zone_isolation_across_warehouses(client, warehouse):
    client.post("/warehouses", json={"id": "wh-002", "name": "Delhi FC-1", "timezone": "Asia/Kolkata"})
    client.post(
        f"/warehouses/{warehouse['id']}/zones",
        json={"id": "zone-001", "name": "Pick Zone A", "zone_type": "picking", "capacity": 15},
    )
    client.post(
        "/warehouses/wh-002/zones",
        json={"id": "zone-999", "name": "Other WH Zone", "zone_type": "picking", "capacity": 5},
    )

    res = client.get(f"/warehouses/{warehouse['id']}/zones")
    ids = [z["id"] for z in res.json()]
    assert "zone-001" in ids
    assert "zone-999" not in ids


def test_tc4_invalid_zone_type_rejected(client, warehouse):
    res = client.post(
        f"/warehouses/{warehouse['id']}/zones",
        json={"id": "zone-x", "name": "Bad", "zone_type": "loading_dock"},
    )
    assert res.status_code == 422


# ---- US-2: Register an employee and certify job roles -----------------------


def test_tc6_create_employee(client, warehouse):
    # "active" is deliberately not used here: the implemented behavior
    # enforces the >=1-role contract (TC-7) at creation time, so an
    # active employee with no role is not "valid employee data". A
    # not-yet-certified new hire is realistically "on_leave" until their
    # first role is attached -- see test_tc8 for the certify-then-activate
    # flow. This is a real ambiguity the test-case doc's original wording
    # left open; flagged in the Feature Doc rather than silently resolved.
    payload = {
        "id": "emp-001",
        "warehouse_id": warehouse["id"],
        "name": "Aditi Rao",
        "employee_type": "full_time",
        "employment_status": "on_leave",
        "hire_date": "2025-01-15",
    }
    res = client.post("/employees", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == "emp-001"
    assert body["name"] == "Aditi Rao"


def test_tc7_active_employee_with_zero_roles_rejected(client, warehouse):
    res = client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "name": "No Role",
            "employee_type": "full_time",
            "employment_status": "active",
        },
    )
    assert res.status_code == 422
    assert "EMPLOYEE_ROLE" in res.json()["detail"]["error"]


def test_tc8_attach_role_satisfies_contract(client, warehouse, job_role):
    # Employee must be created with a non-active status first, since an
    # active employee with zero roles is rejected at creation (TC-7).
    client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "name": "Aditi Rao",
            "employee_type": "full_time",
            "employment_status": "on_leave",
        },
    )

    res = client.post(
        "/employees/emp-001/roles",
        json={"job_role_id": job_role["id"], "certified_date": "2025-01-20", "is_primary": True},
    )
    assert res.status_code == 201

    # Now activating should succeed since the role contract is satisfied.
    res = client.put("/employees/emp-001", json={"employment_status": "active"})
    assert res.status_code == 200
    assert res.json()["employment_status"] == "active"


def test_tc9_multiple_primary_roles_permissive_behavior(client, warehouse, job_role):
    client.post(
        "/job-roles", json={"id": "role-packer", "name": "Packer", "labor_rate": 180.0}
    )
    client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "name": "Aditi Rao",
            "employee_type": "full_time",
            "employment_status": "on_leave",
        },
    )
    r1 = client.post(
        "/employees/emp-001/roles",
        json={"job_role_id": "role-picker", "is_primary": True},
    )
    r2 = client.post(
        "/employees/emp-001/roles",
        json={"job_role_id": "role-packer", "is_primary": True},
    )
    # Documents current (permissive) behavior per Feature Doc Open Questions --
    # no uniqueness constraint on is_primary is enforced yet.
    assert r1.status_code == 201
    assert r2.status_code == 201
    roles = client.get("/employees/emp-001/roles").json()
    assert sum(1 for r in roles if r["is_primary"]) == 2


def test_tc10_invalid_employee_type_rejected(client, warehouse):
    res = client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "name": "Bad Type",
            "employee_type": "seasonal",
            "employment_status": "active",
        },
    )
    assert res.status_code == 422


def test_tc11_invalid_employment_status_rejected(client, warehouse):
    res = client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "name": "Bad Status",
            "employee_type": "full_time",
            "employment_status": "furloughed",
        },
    )
    assert res.status_code == 422


# ---- US-3: Employment status changes are immediately correct ---------------


def _create_active_employee_with_role(client, warehouse, job_role, employee_id="emp-001"):
    client.post(
        "/employees",
        json={
            "id": employee_id,
            "warehouse_id": warehouse["id"],
            "name": "Aditi Rao",
            "employee_type": "full_time",
            "employment_status": "on_leave",
        },
    )
    client.post(f"/employees/{employee_id}/roles", json={"job_role_id": job_role["id"], "is_primary": True})
    client.put(f"/employees/{employee_id}", json={"employment_status": "active"})


def test_tc12_terminate_an_employee(client, warehouse, job_role):
    _create_active_employee_with_role(client, warehouse, job_role)
    res = client.put("/employees/emp-001", json={"employment_status": "terminated"})
    assert res.status_code == 200
    assert res.json()["employment_status"] == "terminated"


def test_tc13_immediate_read_after_write_consistency(client, warehouse, job_role):
    _create_active_employee_with_role(client, warehouse, job_role)
    client.put("/employees/emp-001", json={"employment_status": "terminated"})
    res = client.get("/employees/emp-001")
    assert res.status_code == 200
    assert res.json()["employment_status"] == "terminated"


def test_tc14_filter_excludes_terminated_employees(client, warehouse, job_role):
    _create_active_employee_with_role(client, warehouse, job_role, employee_id="emp-001")
    _create_active_employee_with_role(client, warehouse, job_role, employee_id="emp-002")
    client.put("/employees/emp-001", json={"employment_status": "terminated"})

    res = client.get(f"/employees?warehouse_id={warehouse['id']}&employment_status=active")
    ids = [e["id"] for e in res.json()]
    assert "emp-001" not in ids
    assert "emp-002" in ids


# ---- Feature-wide data quality (ERD reference §5.1) -------------------------


def test_tc18_labor_rate_zero_rejected(client):
    res = client.post("/job-roles", json={"id": "role-x", "name": "Test", "labor_rate": 0})
    assert res.status_code == 422


def test_tc19_negative_labor_rate_rejected(client):
    res = client.post("/job-roles", json={"id": "role-x", "name": "Test", "labor_rate": -5.0})
    assert res.status_code == 422


def test_tc20_missing_required_field_rejected(client, warehouse):
    res = client.post(
        "/employees",
        json={
            "id": "emp-001",
            "warehouse_id": warehouse["id"],
            "employee_type": "full_time",
            "employment_status": "active",
        },
    )
    assert res.status_code == 422
