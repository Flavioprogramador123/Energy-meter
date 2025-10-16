from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.db import get_db
from .. import crud, schemas
from random import randint
from time import sleep


router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/demo")
def create_demo_data(db: Session = Depends(get_db)):
    client = crud.create_client(db, schemas.ClientCreate(name="Cliente Demo"))
    device = crud.create_device(
        db,
        schemas.DeviceCreate(
            client_id=client.id,
            name="PZEM Demo",
            device_type="modbus",
            active=True,
            config={
                "driver": "pzem004t",
                "port": "COM3",
                "slave_id": 1,
                "baudrate": 9600,
                "timeout": 0.5,
                "base": 0,
            },
        ),
    )

    # gerar 40 amostras simuladas (voltage e power)
    for _ in range(40):
        v = 220 + randint(-2, 2)
        p = 120 + randint(-5, 5)
        crud.create_measurement(db, schemas.MeasurementCreate(device_id=device.id, metric="voltage", value=float(v)))
        crud.create_measurement(db, schemas.MeasurementCreate(device_id=device.id, metric="power", value=float(p)))
    return {"client_id": client.id, "device_id": device.id, "samples": 80}




