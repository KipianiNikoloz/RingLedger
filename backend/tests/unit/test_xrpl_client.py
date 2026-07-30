from __future__ import annotations

import httpx
import pytest

from app.integrations.xrpl_client import (
    XrplClient,
    XrplInvalidResponse,
    XrplRpcUnavailable,
    XrplTransactionPending,
    XrplWrongNetwork,
)


def _client(*responses: dict[str, object]) -> XrplClient:
    queued = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=queued.pop(0), request=request)

    return XrplClient(
        rpc_url="https://example.test",
        expected_network_id=1,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_fetch_validated_transaction_returns_server_derived_evidence() -> None:
    client = _client(
        {"result": {"info": {"network_id": 1}}},
        {
            "result": {
                "hash": "ABC12345",
                "validated": True,
                "tx_json": {
                    "TransactionType": "EscrowCreate",
                    "Account": "rOwner",
                    "Destination": "rDestination",
                    "Amount": "5000",
                    "Sequence": 42,
                    "FinishAfter": 800,
                    "date": 900,
                },
                "meta": {"TransactionResult": "tesSUCCESS"},
            }
        },
    )

    evidence = client.fetch_validated_transaction("ABC12345")

    assert evidence.tx_hash == "ABC12345"
    assert evidence.engine_result == "tesSUCCESS"
    assert evidence.tx_json["Sequence"] == 42
    assert evidence.close_time_ripple == 900


def test_fetch_rejects_non_testnet_network() -> None:
    client = _client({"result": {"info": {"network_id": 0}}})

    with pytest.raises(XrplWrongNetwork):
        client.fetch_validated_transaction("ABC12345")


@pytest.mark.parametrize(
    "tx_result",
    [
        {"error": "txnNotFound", "error_message": "Transaction not found."},
        {"hash": "ABC12345", "validated": False, "tx_json": {}, "meta": {}},
    ],
)
def test_fetch_treats_missing_or_unvalidated_transaction_as_pending(tx_result: dict[str, object]) -> None:
    client = _client({"result": {"info": {"network_id": 1}}}, {"result": tx_result})

    with pytest.raises(XrplTransactionPending):
        client.fetch_validated_transaction("ABC12345")


def test_fetch_rejects_malformed_validated_response() -> None:
    client = _client(
        {"result": {"info": {"network_id": 1}}},
        {"result": {"hash": "ABC12345", "validated": True, "tx_json": {}, "meta": {}}},
    )

    with pytest.raises(XrplInvalidResponse):
        client.fetch_validated_transaction("ABC12345")


def test_fetch_maps_transport_errors_to_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = XrplClient(
        rpc_url="https://example.test",
        expected_network_id=1,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(XrplRpcUnavailable):
        client.fetch_validated_transaction("ABC12345")
