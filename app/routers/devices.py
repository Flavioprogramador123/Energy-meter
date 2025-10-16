from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.db import get_db
from .. import crud, schemas


router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
def list_devices(client_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    return [schemas.DeviceRead.model_validate(d) for d in crud.list_devices(db, client_id)]


@router.post("")
def create_device(payload: schemas.DeviceCreate, db: Session = Depends(get_db)):
    obj = crud.create_device(db, payload)
    return schemas.DeviceRead.model_validate(obj)


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    success = crud.delete_device(db, device_id)
    return {"success": success}


@router.patch("/{device_id}")
def update_device(device_id: int, payload: dict, db: Session = Depends(get_db)):
    device = crud.update_device(db, device_id, payload)
    if device:
        return schemas.DeviceRead.model_validate(device)
    return {"error": "Device not found"}

