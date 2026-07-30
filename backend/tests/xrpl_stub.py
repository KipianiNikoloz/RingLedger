from __future__ import annotations

from app.integrations.xrpl_client import XrplTransactionEvidence, XrplTransactionPending


class LedgerStub:
    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        self._evidence: dict[str, XrplTransactionEvidence] = {}
        self._pending: set[str] = set()

    def register(self, evidence: XrplTransactionEvidence, *, validated: bool = True) -> None:
        if validated:
            self._evidence[evidence.tx_hash] = evidence
        else:
            self._pending.add(evidence.tx_hash)

    def fetch_validated_transaction(self, tx_hash: str) -> XrplTransactionEvidence:
        if tx_hash in self._pending:
            raise XrplTransactionPending("xrpl_transaction_pending")
        return self._evidence[tx_hash]


ledger_stub = LedgerStub()
