from __future__ import annotations
from typing import Dict, Any
from .modbus import ModbusRTUClient


def read_pzem004t_metrics(client: ModbusRTUClient, base_address: int = 0) -> Dict[str, Any]:
    """Lê 5 registradores de entrada a partir de base_address e monta métricas do PZEM-004T.

    Convenções adotadas (podem variar conforme revisão):
    - voltage: U16 / 10.0 (V)
    - current: U16 / 1000.0 (A)
    - power:   U16 (W)
    - energy:  U32 (Wh) combinando regs 3 (high) e 4 (low)
    """
    regs = client.read_input_registers(address=base_address, count=5)
    if len(regs) < 5:
        raise ValueError("leituras insuficientes do PZEM-004T")
    voltage_raw, current_raw, power_raw, energy_hi, energy_lo = regs[:5]
    energy_wh = (int(energy_hi) << 16) | int(energy_lo)
    return {
        "voltage": float(voltage_raw) / 10.0,
        "current": float(current_raw) / 1000.0,
        "power": float(power_raw),
        "energy_wh": float(energy_wh),
        "_raw": regs,
    }


