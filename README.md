# Warehouse Labor Planning Tool

See [docs/PRODUCT_OVERVIEW.md](docs/PRODUCT_OVERVIEW.md) for what this is, [docs/RELEASE_PLAN.md](docs/RELEASE_PLAN.md) for the roadmap, and [docs/SOLUTION_ARCHITECTURE.md](docs/SOLUTION_ARCHITECTURE.md) for the technical design. All planning docs live under [docs/](docs/); standing engineering rules are in [CLAUDE.md](CLAUDE.md).

## Running the Sprint 1 demo locally

Requires Python 3.11+ and Node 18+. No external database server, cloud account, or paid service is needed.

```bash
# 1. Create and seed the local mock data source (SQLite)
python db/init_db.py

# 2. Start the backend API (from /backend)
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://127.0.0.1:8000  |  Swagger docs: http://127.0.0.1:8000/docs

# 3. Start the frontend (from /frontend, in a separate terminal)
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

To reset the demo database back to its seeded state at any time:

```bash
python db/init_db.py --reset
```

The SQLite file (`db/labor_planning.db`) is a stand-in for real WMS/WFM/OMS-fed tables — see [docs/SOLUTION_ARCHITECTURE.md](docs/SOLUTION_ARCHITECTURE.md) §1 and §8. It is git-ignored; running `init_db.py` regenerates it from the checked-in `db/schema.sql` and `db/seed_data.sql`.

## What's implemented so far

- **Sprint 1 (BL-1) — Facility & Org Master Data**: warehouse/zone/employee/job-role CRUD, employee-role certification, employment status updates, minimal frontend (Warehouse & Zones view, Employees view). See [docs/features/01-facility-org-master-data.md](docs/features/01-facility-org-master-data.md).
