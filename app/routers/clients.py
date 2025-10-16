from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.db import get_db, Base, engine
from .. import crud, schemas, models


router = APIRouter(prefix="/clients", tags=["clients"])


@router.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)


@router.get("")
def list_clients(db: Session = Depends(get_db)):
    return [schemas.ClientRead.model_validate(c) for c in crud.list_clients(db)]


@router.post("")
def create_client(payload: schemas.ClientCreate, db: Session = Depends(get_db)):
    obj = crud.create_client(db, payload)
    return schemas.ClientRead.model_validate(obj)

