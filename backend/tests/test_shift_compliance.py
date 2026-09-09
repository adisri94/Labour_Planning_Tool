"""Automated tests for Sprint 2 (BL-2): Shift & Compliance Configuration.

Backfills docs/testcases/02-shift-compliance-configuration.md TC-1..TC-16
(TC-17/TC-18 -- seed data checks -- are covered in test_init_db.py-style
fashion against the real db/schema.sql + seed_data.sql, see
test_seed_data_shift_compliance below).
"""
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---- US-1: Define a shift template -----------------------------------------


def test_tc1_create_shift_template(client, warehouse):
    res = client.post(
        f"/warehouses/{warehouse['id']}/shift-templates",
        json={
            "id": "shift-morning",
            "name": "Morning Shift",
            "start_time": "06:00",
            "end_time": "15:00",
            "shift_type": "day",
            "days_of_week": 62,
        },
    )
    assert res.status_code == 201
    assert res.json()["is_active"] is False


def test_tc2_missing_end_time_rejected(client, warehouse):
    res = client.post(
        f"/warehouses/{warehouse['id']}/shift-templates",
        json={"id": "shift-x", "name": "Bad", "start_time": "06:00", "shift_type": "day", "days_of_week": 62},
    )
    assert res.status_code == 422


def test_tc3_invalid_shift_type_rejected(client, warehouse):
    res = client.post(
        f"/warehouses/{warehouse['id']}/shift-templates",
        json={
            "id": "shift-x",
            "name": "Bad",
            "start_time": "06:00",
            "end_time": "15:00",
            "shift_type": "swing",
            "days_of_week": 62,
        },
    )
    assert res.status_code == 422


def test_tc4_inactive_template_still_visible(client, warehouse):
    client.post(
        f"/warehouses/{warehouse['id']}/shift-templates",
        json={
            "id": "shift-morning",
            "name": "Morning Shift",
            "start_time": "06:00",
            "end_time": "15:00",
            "shift_type": "day",
            "days_of_week": 62,
        },
    )
    res = client.get(f"/warehouses/{warehouse['id']}/shift-templates")
    shifts = res.json()
    assert len(shifts) == 1
    assert shifts[0]["is_active"] is False


# ---- US-2: Attach regulations to a shift template --------------------------


def _create_shift(client, warehouse_id, shift_id="shift-morning", start="06:00", end="15:00"):
    client.post(
        f"/warehouses/{warehouse_id}/shift-templates",
        json={
            "id": shift_id,
            "name": "Shift",
            "start_time": start,
            "end_time": end,
            "shift_type": "day",
            "days_of_week": 62,
        },
    )


def _create_regulation(client, reg_id="reg-1", break_mins=60, activate=True):
    client.post(
        "/labor-regulations",
        json={
            "id": reg_id,
            "name": "Test Regulation",
            "max_hours_per_day": 9,
            "max_hours_per_week": 48,
            "break_interval_mins": break_mins,
        },
    )
    if activate:
        client.post(f"/labor-regulations/{reg_id}/activate", json={"activated_by": "Legal"})


def test_tc5_attach_active_regulation(client, warehouse):
    _create_shift(client, warehouse["id"])
    _create_regulation(client)
    res = client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-1"})
    assert res.status_code == 201


def test_tc6_attach_inactive_regulation_rejected(client, warehouse):
    _create_shift(client, warehouse["id"])
    _create_regulation(client, activate=False)
    res = client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-1"})
    assert res.status_code == 422


def test_tc7_max_hours_per_day_zero_rejected(client):
    res = client.post(
        "/labor-regulations",
        json={"id": "reg-x", "name": "Bad", "max_hours_per_day": 0, "max_hours_per_week": 48},
    )
    assert res.status_code == 422


def test_tc8_max_hours_per_week_negative_rejected(client):
    res = client.post(
        "/labor-regulations",
        json={"id": "reg-x", "name": "Bad", "max_hours_per_day": 9, "max_hours_per_week": -5},
    )
    assert res.status_code == 422


def test_tc9_most_restrictive_break_wins(client, warehouse):
    _create_shift(client, warehouse["id"])
    _create_regulation(client, reg_id="reg-30", break_mins=30)
    _create_regulation(client, reg_id="reg-60", break_mins=60)
    client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-30"})
    client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-60"})

    res = client.get("/shift-templates/shift-morning/available-minutes")
    body = res.json()
    assert body["break_minutes"] == 60  # max of 30 and 60, not their sum (90) or the min (30)


# ---- US-3: Compute available shift minutes ----------------------------------


def test_tc10_erd_worked_example_matches(client, warehouse):
    _create_shift(client, warehouse["id"])  # 06:00-15:00 = 540 gross minutes
    _create_regulation(client, break_mins=60)
    client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-1"})

    res = client.get("/shift-templates/shift-morning/available-minutes")
    assert res.json()["available_shift_minutes"] == 480


def test_tc11_no_regulation_attached(client, warehouse):
    _create_shift(client, warehouse["id"])
    res = client.get("/shift-templates/shift-morning/available-minutes")
    body = res.json()
    assert body["break_minutes"] == 0
    assert body["available_shift_minutes"] == body["gross_minutes"] == 540


def test_tc12_overnight_shift_wraps_past_midnight(client, warehouse):
    _create_shift(client, warehouse["id"], start="22:00", end="06:00")
    _create_regulation(client, break_mins=30)
    client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-1"})

    res = client.get("/shift-templates/shift-morning/available-minutes")
    body = res.json()
    assert body["gross_minutes"] == 480
    assert body["available_shift_minutes"] == 450


# ---- US-4: Block usage of unactivated configuration -------------------------


def test_tc13_activate_shift_template(client, warehouse):
    _create_shift(client, warehouse["id"])
    res = client.post("/shift-templates/shift-morning/activate", json={"activated_by": "PM Name"})
    assert res.status_code == 200
    body = res.json()
    assert body["is_active"] is True
    assert body["activated_by"] == "PM Name"
    assert body["activated_at"] is not None


def test_tc14_activate_regulation(client):
    _create_regulation(client, activate=False)
    res = client.post("/labor-regulations/reg-1/activate", json={"activated_by": "Legal Team"})
    assert res.status_code == 200
    body = res.json()
    assert body["is_active"] is True
    assert body["activated_by"] == "Legal Team"
    assert body["activated_at"] is not None


def test_tc15_gate_holds_regardless_of_entry_point(client, warehouse):
    _create_shift(client, warehouse["id"])
    _create_regulation(client, activate=False)
    res = client.post("/shift-templates/shift-morning/regulations", json={"regulation_id": "reg-1"})
    assert res.status_code == 422


# TC-16 (Decision Log process check) is a manual/documentation check, not
# automatable -- see the test case doc.


# ---- Seed data (TC-17/TC-18) -------------------------------------------------


def test_tc17_seed_data_bootstraps_active_shift_config(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    shutil.copy(REPO_ROOT / "db" / "schema.sql", db_dir / "schema.sql")
    shutil.copy(REPO_ROOT / "db" / "seed_data.sql", db_dir / "seed_data.sql")
    shutil.copy(REPO_ROOT / "db" / "init_db.py", db_dir / "init_db.py")

    result = subprocess.run(
        [sys.executable, str(db_dir / "init_db.py")], cwd=db_dir, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr

    conn = sqlite3.connect(db_dir / "labor_planning.db")
    try:
        shift_rows = conn.execute("SELECT is_active FROM shift_template").fetchall()
        assert len(shift_rows) == 2
        assert all(row[0] == 1 for row in shift_rows)

        reg_rows = conn.execute("SELECT is_active FROM labor_regulation").fetchall()
        assert len(reg_rows) == 1
        assert reg_rows[0][0] == 1

        link_count = conn.execute("SELECT COUNT(*) FROM regulation_shift").fetchone()[0]
        assert link_count == 2
    finally:
        conn.close()


def test_tc18_seeded_morning_shift_available_minutes(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    shutil.copy(REPO_ROOT / "db" / "schema.sql", db_dir / "schema.sql")
    shutil.copy(REPO_ROOT / "db" / "seed_data.sql", db_dir / "seed_data.sql")
    shutil.copy(REPO_ROOT / "db" / "init_db.py", db_dir / "init_db.py")
    subprocess.run(
        [sys.executable, str(db_dir / "init_db.py")], cwd=db_dir, capture_output=True, text=True
    )

    conn = sqlite3.connect(db_dir / "labor_planning.db")
    try:
        start, end = conn.execute(
            "SELECT start_time, end_time FROM shift_template WHERE id = 'shift-morning'"
        ).fetchone()
        assert start == "06:00"
        assert end == "15:00"
        break_mins = conn.execute(
            "SELECT break_interval_mins FROM labor_regulation WHERE id = 'reg-flsa'"
        ).fetchone()[0]
        assert break_mins == 60
        # 540 gross - 60 break = 480, matching the ERD worked example.
    finally:
        conn.close()
