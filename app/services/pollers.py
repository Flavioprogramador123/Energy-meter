from __future__ import annotations
from sqlalchemy.orm import Session
from ..core.db import SessionLocal
from .. import crud, schemas, models
from ..connectors.modbus import ModbusRTUClient, ModbusTCPClient
from ..connectors.pzem004t import read_pzem004t_metrics
from ..connectors.eastron_sdm630 import read_sdm630_metrics


def poll_modbus_devices():
    """Poller para dispositivos Modbus RTU (serial)."""
    db: Session = SessionLocal()
    try:
        devices = crud.list_devices(db)
        for d in devices:
            if d.device_type != "modbus" or not d.active:
                continue
            cfg = d.config or {}
            try:
                with ModbusRTUClient(
                    port=cfg.get("port", "COM3"),
                    slave_id=int(cfg.get("slave_id", 1)),
                    baudrate=int(cfg.get("baudrate", 9600)),
                    timeout=float(cfg.get("timeout", 0.5)),
                ) as client:
                    if cfg.get("driver") == "pzem004t":
                        values = read_pzem004t_metrics(client, base_address=int(cfg.get("base", 0)))
                        for k in ["voltage", "current", "power", "energy_wh"]:
                            if k in values:
                                crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=k, value=float(values[k])))
                    elif cfg.get("driver") == "sdm630":
                        values = read_sdm630_metrics(client, base_address=int(cfg.get("base", 0)))
                        for k, v in values.items():
                            if not k.startswith("_") and isinstance(v, (int, float)):
                                crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=k, value=float(v)))
                    else:
                        # leitura genérica de regs
                        regs = client.read_input_registers(address=int(cfg.get("base", 0)), count=int(cfg.get("count", 4)))
                        metrics = cfg.get("metrics", ["voltage", "current", "power", "energy_wh"])
                        for idx, val in enumerate(regs):
                            metric = metrics[idx] if idx < len(metrics) else f"reg_{idx}"
                            crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=metric, value=float(val)))
            except Exception as e:
                print(f"Erro ao ler dispositivo Modbus RTU {d.id} ({d.name}): {e}")
                continue
        db.commit()
    finally:
        db.close()


def poll_modbus_tcp_devices():
    """Poller para dispositivos Modbus TCP (Elfin-EW11A, conversores RS485-WiFi, etc)."""
    db: Session = SessionLocal()
    try:
        devices = crud.list_devices(db)
        for d in devices:
            if d.device_type != "modbus_tcp" or not d.active:
                continue
            cfg = d.config or {}
            try:
                with ModbusTCPClient(
                    host=cfg.get("host", "192.168.1.100"),
                    port=int(cfg.get("port", 502)),
                    slave_id=int(cfg.get("slave_id", 1)),
                    timeout=float(cfg.get("timeout", 3.0)),
                ) as client:
                    if cfg.get("driver") == "pzem004t":
                        values = read_pzem004t_metrics(client, base_address=int(cfg.get("base", 0)))
                        for k in ["voltage", "current", "power", "energy_wh"]:
                            if k in values:
                                crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=k, value=float(values[k])))
                    elif cfg.get("driver") == "sdm630":
                        values = read_sdm630_metrics(client, base_address=int(cfg.get("base", 0)))
                        for k, v in values.items():
                            if not k.startswith("_") and isinstance(v, (int, float)):
                                crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=k, value=float(v)))
                    else:
                        # leitura genérica de regs
                        regs = client.read_input_registers(address=int(cfg.get("base", 0)), count=int(cfg.get("count", 4)))
                        metrics = cfg.get("metrics", ["voltage", "current", "power", "energy_wh"])
                        for idx, val in enumerate(regs):
                            metric = metrics[idx] if idx < len(metrics) else f"reg_{idx}"
                            crud.create_measurement(db, schemas.MeasurementCreate(device_id=d.id, metric=metric, value=float(val)))
            except Exception as e:
                print(f"Erro ao ler dispositivo Modbus TCP {d.id} ({d.name}): {e}")
                continue
        db.commit()
    finally:
        db.close()

