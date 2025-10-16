from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.db import get_db
from .. import crud, schemas
from ..services.forwarder import Forwarder
from ..core.config import settings
from ..services.alarms import eval_operator
from ..models import AlarmRuleModel


router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("")
async def ingest_payload(payload: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    obj = crud.create_measurement(db, payload)

    # avaliar regras aplicáveis
    device = crud.get_device(db, payload.device_id)
    if device is not None:
        rules = db.query(AlarmRuleModel).filter(
            AlarmRuleModel.enabled == True,
            AlarmRuleModel.metric == payload.metric,
            (AlarmRuleModel.device_id == None) | (AlarmRuleModel.device_id == payload.device_id),
            AlarmRuleModel.client_id == device.client_id,
        ).all()
        for r in rules:
            try:
                if eval_operator(r.operator, payload.value, r.threshold):
                    crud.create_alarm_event(db, r.id, device.id, payload.metric, payload.value, details={"op": r.operator, "threshold": r.threshold})
            except Exception:
                # ignorar erro em regra individual para não interromper ingestão
                pass

    # encaminhar se habilitado
    if settings.enable_forwarding and settings.forwarder_url:
        fwd = Forwarder(settings.forwarder_url)
        try:
            await fwd.forward_measurement(payload.model_dump())
        except Exception:
            pass

    return schemas.MeasurementRead.model_validate(obj)

