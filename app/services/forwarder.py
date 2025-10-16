from __future__ import annotations
from typing import Optional
import httpx


class Forwarder:
    def __init__(self, base_url: Optional[str]):
        self.base_url = base_url.rstrip("/") if base_url else None

    async def forward_measurement(self, payload: dict) -> dict:
        if not self.base_url:
            return {"forwarded": False, "reason": "no_base_url"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(f"{self.base_url}/api/ingest", json=payload)
            return {"forwarded": r.status_code < 300, "status": r.status_code}



