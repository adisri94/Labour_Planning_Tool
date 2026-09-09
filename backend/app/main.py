"""FastAPI entrypoint -- Sprint 1 (BL-1) + Sprint 2 (BL-2).

Run: uvicorn app.main:app --reload (from the /backend directory).
Requires db/labor_planning.db to already exist -- run `python db/init_db.py` first.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import employees, job_roles, labor_regulations, shift_templates, warehouses

app = FastAPI(
    title="Warehouse Labor Planning Tool API",
    description="Sprint 1: Facility & Org Master Data. Sprint 2: Shift & Compliance Configuration.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    # Regex (not a fixed list) so the local dev frontend can run on whichever
    # port Vite ends up bound to (e.g. if 5173 is already taken).
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(warehouses.router)
app.include_router(job_roles.router)
app.include_router(employees.router)
app.include_router(shift_templates.router)
app.include_router(labor_regulations.router)


@app.get("/health")
def health():
    return {"status": "ok"}
