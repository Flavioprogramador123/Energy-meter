from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ClientCreate(BaseModel):
    name: str
    external_id: Optional[str] = None


class ClientRead(BaseModel):
    id: int
    name: str
    external_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    client_id: int
    name: str
    device_type: str
    active: bool = True
    config: dict | None = None


class DeviceRead(BaseModel):
    id: int
    client_id: int
    name: str
    device_type: str
    active: bool
    config: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    device_id: int
    timestamp: datetime | None = None
    metric: str
    value: float
    extra: dict | None = None


class MeasurementRead(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    metric: str
    value: float
    extra: dict | None

    class Config:
        from_attributes = True


class AlarmRuleCreate(BaseModel):
    client_id: Optional[int] = None
    device_id: Optional[int] = None
    name: str
    metric: str
    operator: str = Field(pattern=r"^(==|!=|>=|<=|>|<)$")
    threshold: float
    enabled: bool = True


class AlarmRuleRead(BaseModel):
    id: int
    client_id: int
    device_id: Optional[int]
    name: str
    metric: str
    operator: str
    threshold: float
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlarmEventRead(BaseModel):
    id: int
    rule_id: int
    device_id: int
    timestamp: datetime
    metric: str
    value: float
    details: dict | None
    acknowledged: bool

    class Config:
        from_attributes = True

