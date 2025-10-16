from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.db import get_db
from .. import crud, schemas
from ..models import AlarmEvent


router = APIRouter(prefix="/alarms", tags=["alarms"])


@router.get("/rules")
def list_alarm_rules(client_id: int | None = Query(default=None), device_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    rows = crud.list_alarm_rules(db, client_id=client_id, device_id=device_id)
    return [schemas.AlarmRuleRead.model_validate(r) for r in rows]


@router.post("/rules")
def create_alarm_rule(payload: schemas.AlarmRuleCreate, db: Session = Depends(get_db)):
    obj = crud.create_alarm_rule(db, payload)
    return schemas.AlarmRuleRead.model_validate(obj)


@router.delete("/rules/{rule_id}")
def delete_alarm_rule(rule_id: int, db: Session = Depends(get_db)):
    from .. import models
    rule = db.query(models.AlarmRuleModel).filter(models.AlarmRuleModel.id == rule_id).first()
    if not rule:
        return {"error": "Regra não encontrada"}
    db.delete(rule)
    db.commit()
    return {"message": "Regra removida com sucesso"}


@router.get("/events")
def list_alarm_events(device_id: int | None = Query(default=None), limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(AlarmEvent)
    if device_id is not None:
        q = q.filter(AlarmEvent.device_id == device_id)
    rows = q.order_by(AlarmEvent.timestamp.desc()).limit(limit).all()
    return rows

