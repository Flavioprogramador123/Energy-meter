from __future__ import annotations
from typing import Any
import tinytuya


class TuyaAPIClient:
    def __init__(self, api_region: str, api_key: str, api_secret: str, api_uid: str):
        self.client = tinytuya.Cloud(
            apiRegion=api_region,
            apiKey=api_key,
            apiSecret=api_secret,
            apiDeviceID=api_uid,
        )

    def list_devices(self) -> list[dict[str, Any]]:
        data = self.client.getdevices()
        return data or []

    def get_status(self, device_id: str) -> dict[str, Any]:
        status = self.client.getstatus(device_id)
        return status or {}

    def get_energy_data(self, device_id: str) -> dict[str, Any]:
        # Placeholder genérico; alguns dispositivos Tuya expõem dps específicos (p.ex 101, 102)
        return self.get_status(device_id)

