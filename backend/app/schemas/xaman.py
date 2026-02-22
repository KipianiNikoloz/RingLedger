from __future__ import annotations

from pydantic import BaseModel


class XamanSignRequestView(BaseModel):
    payload_id: str
    deep_link_url: str
    qr_png_url: str
    websocket_status_url: str | None = None
    mode: str
