"""FastAPI entrypoint -- Sprint 1 (BL-1): Facility & Org Master Data.

Run: uvicorn app.main:app --reload (from the /backend directory).
Requires db/labor_planning.db to already exist -- run `python db/init_db.py` first.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import employees, job_roles, warehouses

app = FastAPI(
    title="Warehouse Labor Planning Tool API",
    description="Sprint 1: Facility & Org Master Data",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(warehouses.router)
app.include_router(job_roles.router)
app.include_router(employees.router)


@app.get("/health")
def health():
    return {"status": "ok"}
