from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class XrplClientError(RuntimeError):
    """Base error for authoritative XRPL lookups."""


class XrplRpcUnavailable(XrplClientError):
    """The configured XRPL node could not serve the request."""


class XrplTransactionPending(XrplClientError):
    """The transaction is not yet present in a validated ledger."""


class XrplInvalidResponse(XrplClientError):
    """The XRPL node returned an unusable response."""


class XrplWrongNetwork(XrplClientError):
    """The configured XRPL node is not the expected network."""


@dataclass(frozen=True)
class XrplTransactionEvidence:
    tx_hash: str
    engine_result: str
    tx_json: dict[str, Any]
    close_time_ripple: int | None


class XrplClient:
    def __init__(
        self,
        *,
        rpc_url: str,
        expected_network_id: int,
        timeout_seconds: float = 10,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._rpc_url = rpc_url
        self._expected_network_id = expected_network_id
        self._client = http_client or httpx.Client(timeout=timeout_seconds)

    def fetch_validated_transaction(self, tx_hash: str) -> XrplTransactionEvidence:
        server_info = self._request("server_info")
        info = server_info.get("info")
        if not isinstance(info, dict) or not isinstance(info.get("network_id"), int):
            raise XrplInvalidResponse("xrpl_network_id_missing")
        if info["network_id"] != self._expected_network_id:
            raise XrplWrongNetwork("xrpl_wrong_network")

        result = self._request("tx", {"transaction": tx_hash, "binary": False, "api_version": 2})
        if result.get("error") == "txnNotFound":
            raise XrplTransactionPending("xrpl_transaction_pending")
        if result.get("validated") is not True:
            raise XrplTransactionPending("xrpl_transaction_pending")

        returned_hash = result.get("hash")
        tx_json = result.get("tx_json")
        meta = result.get("meta")
        if returned_hash != tx_hash or not isinstance(tx_json, dict) or not isinstance(meta, dict):
            raise XrplInvalidResponse("xrpl_transaction_malformed")
        engine_result = meta.get("TransactionResult")
        if not isinstance(engine_result, str):
            raise XrplInvalidResponse("xrpl_transaction_result_missing")

        close_time = tx_json.get("date", result.get("date"))
        if close_time is not None and not isinstance(close_time, int):
            raise XrplInvalidResponse("xrpl_close_time_invalid")
        return XrplTransactionEvidence(
            tx_hash=returned_hash,
            engine_result=engine_result,
            tx_json=tx_json,
            close_time_ripple=close_time,
        )

    def _request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self._client.post(
                self._rpc_url,
                json={"method": method, "params": [params or {}]},
            )
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise XrplRpcUnavailable("xrpl_rpc_unavailable") from exc
        if not isinstance(body, dict) or not isinstance(body.get("result"), dict):
            raise XrplInvalidResponse("xrpl_response_malformed")
        return body["result"]
