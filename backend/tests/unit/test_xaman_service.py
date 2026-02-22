from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from app.integrations.xaman_service import XamanIntegrationError, XamanService


class _FakeHttpResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> _FakeHttpResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(self._payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


class XamanServiceUnitTests(unittest.TestCase):
    def test_stub_sign_request_is_deterministic(self) -> None:
        service = XamanService(
            mode="stub",
            api_base_url="https://xumm.app",
            api_key=None,
            api_secret=None,
            timeout_seconds=5,
        )
        tx_json = {"Account": "rTest", "Amount": "1000", "TransactionType": "EscrowCreate"}

        one = service.create_sign_request(tx_json=tx_json, reference="escrow:1")
        two = service.create_sign_request(tx_json=tx_json, reference="escrow:1")
        other = service.create_sign_request(tx_json=tx_json, reference="escrow:2")

        self.assertEqual(one.payload_id, two.payload_id)
        self.assertNotEqual(one.payload_id, other.payload_id)
        self.assertTrue(one.deep_link_url.startswith("xumm://payload/"))
        self.assertTrue(one.qr_png_url.startswith("https://xumm.app/sign/"))
        self.assertEqual(one.mode, "stub")

    def test_api_mode_requires_credentials(self) -> None:
        service = XamanService(
            mode="api",
            api_base_url="https://xumm.app",
            api_key=None,
            api_secret=None,
            timeout_seconds=5,
        )
        with self.assertRaises(XamanIntegrationError):
            service.create_sign_request(tx_json={"TransactionType": "EscrowCreate"}, reference="escrow:1")

    @patch("app.integrations.xaman_service.urlopen")
    def test_api_mode_parses_sign_request_response(self, urlopen_mock: object) -> None:
        urlopen_mock.return_value = _FakeHttpResponse(
            payload={
                "uuid": "1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650",
                "next": {"always": "https://xumm.app/sign/1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650"},
                "refs": {
                    "qr_png": "https://xumm.app/sign/1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650/qr.png",
                    "websocket_status": "wss://xumm.app/sign/1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650",
                },
            }
        )
        service = XamanService(
            mode="api",
            api_base_url="https://xumm.app",
            api_key="test-key",
            api_secret="test-secret",
            timeout_seconds=5,
        )

        result = service.create_sign_request(
            tx_json={"TransactionType": "EscrowCreate", "Account": "rTest"},
            reference="escrow:1",
        )

        self.assertEqual(result.payload_id, "1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650")
        self.assertEqual(result.deep_link_url, "https://xumm.app/sign/1f9f9eaf-1566-4ef5-a2a4-c6a5a1dd8650")
        self.assertEqual(result.mode, "api")


if __name__ == "__main__":
    unittest.main()
