from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Warehouse, Zone
from app.schemas.master_data import (
    WarehouseCreate,
    WarehouseOut,
    WarehouseUpdate,
    ZoneCreate,
    ZoneOut,
    ZoneUpdate,
)

router = APIRouter(tags=["warehouses"])


@router.post("/warehouses", response_model=WarehouseOut, status_code=201)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)):
    if db.get(Warehouse, payload.id) is not None:
        raise HTTPException(status_code=409, detail={"error": "Warehouse id already exists", "field": "id"})
    warehouse = Warehouse(**payload.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get("/warehouses", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: str, db: Session = Depends(get_db)):
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: str, payload: WarehouseUpdate, db: Session = Depends(get_db)):
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.post("/warehouses/{warehouse_id}/zones", response_model=ZoneOut, status_code=201)
def create_zone(warehouse_id: str, payload: ZoneCreate, db: Session = Depends(get_db)):
    if db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    if db.get(Zone, payload.id) is not None:
        raise HTTPException(status_code=409, detail={"error": "Zone id already exists", "field": "id"})
    zone = Zone(warehouse_id=warehouse_id, **payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/warehouses/{warehouse_id}/zones", response_model=list[ZoneOut])
def list_zones(warehouse_id: str, db: Session = Depends(get_db)):
    if db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    return db.query(Zone).filter(Zone.warehouse_id == warehouse_id).all()


@router.put("/zones/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: str, payload: ZoneUpdate, db: Session = Depends(get_db)):
    zone = db.get(Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail={"error": "Zone not found"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    return zone
