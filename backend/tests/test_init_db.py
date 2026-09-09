"""Automated tests for db/init_db.py -- backfills
docs/testcases/01-facility-org-master-data.md TC-15..TC-17.

Runs the real script as a subprocess against a temp copy of schema.sql /
seed_data.sql, so it never touches the actual demo db/labor_planning.db.
"""
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_init_db(db_dir, *extra_args):
    return subprocess.run(
        [sys.executable, str(db_dir / "init_db.py"), *extra_args],
        cwd=db_dir,
        capture_output=True,
        text=True,
    )


def _make_temp_db_dir(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    shutil.copy(REPO_ROOT / "db" / "schema.sql", db_dir / "schema.sql")
    shutil.copy(REPO_ROOT / "db" / "seed_data.sql", db_dir / "seed_data.sql")
    shutil.copy(REPO_ROOT / "db" / "init_db.py", db_dir / "init_db.py")
    return db_dir


def test_tc15_fresh_db_bootstrap(tmp_path):
    db_dir = _make_temp_db_dir(tmp_path)
    result = _run_init_db(db_dir)
    assert result.returncode == 0, result.stderr
    assert (db_dir / "labor_planning.db").exists()


def test_tc16_seed_data_completeness(tmp_path):
    db_dir = _make_temp_db_dir(tmp_path)
    _run_init_db(db_dir)

    conn = sqlite3.connect(db_dir / "labor_planning.db")
    try:
        assert conn.execute("SELECT COUNT(*) FROM warehouse").fetchone()[0] >= 1
        zone_count = conn.execute("SELECT COUNT(*) FROM zone").fetchone()[0]
        assert 3 <= zone_count <= 4
        role_count = conn.execute("SELECT COUNT(*) FROM job_role").fetchone()[0]
        assert 3 <= role_count <= 4
        employee_count = conn.execute("SELECT COUNT(*) FROM employee").fetchone()[0]
        assert 10 <= employee_count <= 15

        employees_without_roles = conn.execute(
            """
            SELECT COUNT(*) FROM employee e
            WHERE NOT EXISTS (
                SELECT 1 FROM employee_role er WHERE er.employee_id = e.id
            )
            """
        ).fetchone()[0]
        assert employees_without_roles == 0
    finally:
        conn.close()


def test_tc17_rerun_against_existing_db_does_not_duplicate(tmp_path):
    db_dir = _make_temp_db_dir(tmp_path)
    _run_init_db(db_dir)

    conn = sqlite3.connect(db_dir / "labor_planning.db")
    before = conn.execute("SELECT COUNT(*) FROM employee").fetchone()[0]
    conn.close()

    # Re-running without --reset must not silently duplicate rows: current
    # behavior is a clear, non-zero exit with no changes made to the file.
    result = _run_init_db(db_dir)
    assert result.returncode != 0

    conn = sqlite3.connect(db_dir / "labor_planning.db")
    after = conn.execute("SELECT COUNT(*) FROM employee").fetchone()[0]
    conn.close()
    assert after == before

    # --reset explicitly re-seeds deterministically (also no duplication).
    result = _run_init_db(db_dir, "--reset")
    assert result.returncode == 0
    conn = sqlite3.connect(db_dir / "labor_planning.db")
    after_reset = conn.execute("SELECT COUNT(*) FROM employee").fetchone()[0]
    conn.close()
    assert after_reset == before
