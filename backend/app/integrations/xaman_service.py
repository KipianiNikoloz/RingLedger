from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class XamanIntegrationError(RuntimeError):
    """Raised when Xaman sign-request creation cannot be completed safely."""


@dataclass(frozen=True)
class XamanSignRequest:
    payload_id: str
    deep_link_url: str
    qr_png_url: str
    websocket_status_url: str | None
    mode: str


class XamanPayloadStatus(StrEnum):
    OPEN = "open"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class XamanPayloadStatusResult:
    payload_id: str
    status: XamanPayloadStatus
    tx_hash: str | None
    mode: str


@dataclass(frozen=True)
class XamanService:
    mode: str
    api_base_url: str
    api_key: str | None
    api_secret: str | None
    timeout_seconds: int = 10

    @classmethod
    def from_settings(cls) -> XamanService:
        return cls(
            mode=settings.xaman_mode,
            api_base_url=settings.xaman_api_base_url,
            api_key=settings.xaman_api_key,
            api_secret=settings.xaman_api_secret,
            timeout_seconds=settings.xaman_timeout_seconds,
        )

    def create_sign_request(self, *, tx_json: dict[str, Any], reference: str) -> XamanSignRequest:
        if self.mode == "stub":
            return self._create_stub_sign_request(tx_json=tx_json, reference=reference)
        if self.mode != "api":
            raise XamanIntegrationError("xaman_mode_invalid")
        if not self.api_key or not self.api_secret:
            raise XamanIntegrationError("xaman_api_credentials_missing")
        return self._create_api_sign_request(tx_json=tx_json, reference=reference)

    def get_payload_status(
        self,
        *,
        payload_id: str,
        observed_status: str | None = None,
        observed_tx_hash: str | None = None,
    ) -> XamanPayloadStatusResult:
        if self.mode == "stub":
            status = _parse_observed_status(observed_status)
            tx_hash = observed_tx_hash.strip() if observed_tx_hash else None
            return XamanPayloadStatusResult(payload_id=payload_id, status=status, tx_hash=tx_hash, mode="stub")
        if self.mode != "api":
            raise XamanIntegrationError("xaman_mode_invalid")
        if not self.api_key or not self.api_secret:
            raise XamanIntegrationError("xaman_api_credentials_missing")
        return self._get_api_payload_status(payload_id=payload_id)

    def _create_stub_sign_request(self, *, tx_json: dict[str, Any], reference: str) -> XamanSignRequest:
        serialized = json.dumps(tx_json, separators=(",", ":"), sort_keys=True, ensure_ascii=True)
        payload_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{reference}:{serialized}"))
        return XamanSignRequest(
            payload_id=payload_id,
            deep_link_url=f"xumm://payload/{payload_id}",
            qr_png_url=f"https://xumm.app/sign/{payload_id}/qr.png",
            websocket_status_url=f"wss://xumm.app/sign/{payload_id}",
            mode="stub",
        )

    def _create_api_sign_request(self, *, tx_json: dict[str, Any], reference: str) -> XamanSignRequest:
        url = f"{self.api_base_url.rstrip('/')}/api/v1/platform/payload"
        payload_body = {
            "txjson": tx_json,
            "options": {"submit": True},
            "custom_meta": {"identifier": reference},
        }
        body_raw = json.dumps(payload_body, separators=(",", ":"), sort_keys=True, ensure_ascii=True).encode("utf-8")
        request = Request(url=url, data=body_raw, method="POST")
        request.add_header("Content-Type", "application/json")
        request.add_header("X-API-Key", self.api_key)
        request.add_header("X-API-Secret", self.api_secret)

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise XamanIntegrationError("xaman_api_http_error") from exc
        except URLError as exc:
            raise XamanIntegrationError("xaman_api_connection_error") from exc
        except json.JSONDecodeError as exc:
            raise XamanIntegrationError("xaman_api_invalid_json") from exc

        payload_id = response_payload.get("uuid")
        next_data = response_payload.get("next")
        refs_data = response_payload.get("refs")
        if not isinstance(payload_id, str):
            raise XamanIntegrationError("xaman_api_invalid_response")
        if not isinstance(next_data, dict):
            raise XamanIntegrationError("xaman_api_invalid_response")
        if not isinstance(refs_data, dict):
            raise XamanIntegrationError("xaman_api_invalid_response")

        deep_link_url = next_data.get("always")
        qr_png_url = refs_data.get("qr_png")
        websocket_status_url = refs_data.get("websocket_status")
        if not isinstance(deep_link_url, str) or not isinstance(qr_png_url, str):
            raise XamanIntegrationError("xaman_api_invalid_response")
        if websocket_status_url is not None and not isinstance(websocket_status_url, str):
            raise XamanIntegrationError("xaman_api_invalid_response")

        return XamanSignRequest(
            payload_id=payload_id,
            deep_link_url=deep_link_url,
            qr_png_url=qr_png_url,
            websocket_status_url=websocket_status_url,
            mode="api",
        )

    def _get_api_payload_status(self, *, payload_id: str) -> XamanPayloadStatusResult:
        url = f"{self.api_base_url.rstrip('/')}/api/v1/platform/payload/{payload_id}"
        request = Request(url=url, method="GET")
        request.add_header("X-API-Key", self.api_key)
        request.add_header("X-API-Secret", self.api_secret)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise XamanIntegrationError("xaman_api_http_error") from exc
        except URLError as exc:
            raise XamanIntegrationError("xaman_api_connection_error") from exc
        except json.JSONDecodeError as exc:
            raise XamanIntegrationError("xaman_api_invalid_json") from exc

        status = _parse_api_payload_status(response_payload)
        tx_hash = _extract_api_tx_hash(response_payload)
        return XamanPayloadStatusResult(payload_id=payload_id, status=status, tx_hash=tx_hash, mode="api")


def _parse_observed_status(observed_status: str | None) -> XamanPayloadStatus:
    if observed_status is None:
        return XamanPayloadStatus.OPEN
    normalized = observed_status.strip().lower()
    if normalized == XamanPayloadStatus.OPEN.value:
        return XamanPayloadStatus.OPEN
    if normalized == XamanPayloadStatus.SIGNED.value:
        return XamanPayloadStatus.SIGNED
    if normalized == XamanPayloadStatus.DECLINED.value:
        return XamanPayloadStatus.DECLINED
    if normalized == XamanPayloadStatus.EXPIRED.value:
        return XamanPayloadStatus.EXPIRED
    if normalized == XamanPayloadStatus.UNKNOWN.value:
        return XamanPayloadStatus.UNKNOWN
    raise XamanIntegrationError("xaman_observed_status_invalid")


def _parse_api_payload_status(payload: dict[str, Any]) -> XamanPayloadStatus:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        raise XamanIntegrationError("xaman_api_invalid_response")

    resolved = bool(meta.get("resolved"))
    signed = bool(meta.get("signed"))
    cancelled = bool(meta.get("cancelled"))
    expired = bool(meta.get("expired"))

    if signed:
        return XamanPayloadStatus.SIGNED
    if cancelled:
        return XamanPayloadStatus.DECLINED
    if expired:
        return XamanPayloadStatus.EXPIRED
    if resolved and not signed:
        return XamanPayloadStatus.DECLINED
    return XamanPayloadStatus.OPEN


def _extract_api_tx_hash(payload: dict[str, Any]) -> str | None:
    response = payload.get("response")
    if not isinstance(response, dict):
        return None
    tx_hash = response.get("txid") or response.get("txid_hex")
    if isinstance(tx_hash, str):
        normalized = tx_hash.strip()
        return normalized or None
    return None
