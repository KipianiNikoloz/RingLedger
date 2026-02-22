from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.integrations.xaman_service import XamanPayloadStatus, XamanService
from app.models.audit_log import AuditLog
from app.models.bout import Bout
from app.models.enums import EscrowKind
from app.models.escrow import Escrow
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository


@dataclass(frozen=True)
class SigningReconciliationOutcome:
    bout: Bout
    escrow: Escrow
    payload_id: str
    signing_status: XamanPayloadStatus
    tx_hash: str | None


@dataclass
class SigningReconciliationService:
    session: Session
    xaman_service: XamanService = field(default_factory=XamanService.from_settings)
    bouts: BoutRepository = field(init=False)
    escrows: EscrowRepository = field(init=False)
    audit_logs: AuditLogRepository = field(init=False)

    def __post_init__(self) -> None:
        self.bouts = BoutRepository(session=self.session)
        self.escrows = EscrowRepository(session=self.session)
        self.audit_logs = AuditLogRepository(session=self.session)

    def reconcile_escrow_create_signing(
        self,
        *,
        bout_id: uuid.UUID,
        escrow_kind: EscrowKind,
        payload_id: str,
        actor_user_id: uuid.UUID,
        observed_status: str | None,
        observed_tx_hash: str | None,
    ) -> SigningReconciliationOutcome:
        return self._reconcile(
            bout_id=bout_id,
            escrow_kind=escrow_kind,
            payload_id=payload_id,
            actor_user_id=actor_user_id,
            observed_status=observed_status,
            observed_tx_hash=observed_tx_hash,
            action="escrow_signing_reconcile",
        )

    def reconcile_payout_signing(
        self,
        *,
        bout_id: uuid.UUID,
        escrow_kind: EscrowKind,
        payload_id: str,
        actor_user_id: uuid.UUID,
        observed_status: str | None,
        observed_tx_hash: str | None,
    ) -> SigningReconciliationOutcome:
        return self._reconcile(
            bout_id=bout_id,
            escrow_kind=escrow_kind,
            payload_id=payload_id,
            actor_user_id=actor_user_id,
            observed_status=observed_status,
            observed_tx_hash=observed_tx_hash,
            action="payout_signing_reconcile",
        )

    def _reconcile(
        self,
        *,
        bout_id: uuid.UUID,
        escrow_kind: EscrowKind,
        payload_id: str,
        actor_user_id: uuid.UUID,
        observed_status: str | None,
        observed_tx_hash: str | None,
        action: str,
    ) -> SigningReconciliationOutcome:
        bout = self.bouts.get(bout_id=bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        escrow = self.escrows.get_for_bout_kind(bout_id=bout_id, escrow_kind=escrow_kind)
        if escrow is None:
            raise ValueError("escrow_not_found")

        status_result = self.xaman_service.get_payload_status(
            payload_id=payload_id,
            observed_status=observed_status,
            observed_tx_hash=observed_tx_hash,
        )
        self._apply_failure_classification(
            escrow=escrow,
            payload_id=status_result.payload_id,
            status=status_result.status,
            tx_hash=status_result.tx_hash,
        )

        outcome = _status_to_outcome(status_result.status)
        self._append_audit_entry(
            actor_user_id=actor_user_id,
            action=action,
            entity_id=str(escrow.id),
            outcome=outcome,
            details={
                "bout_id": str(bout.id),
                "escrow_kind": escrow.kind.value,
                "escrow_status": escrow.status.value,
                "payload_id": status_result.payload_id,
                "signing_status": status_result.status.value,
                "tx_hash": status_result.tx_hash,
                "failure_code": escrow.failure_code,
                "mode": status_result.mode,
            },
        )
        return SigningReconciliationOutcome(
            bout=bout,
            escrow=escrow,
            payload_id=status_result.payload_id,
            signing_status=status_result.status,
            tx_hash=status_result.tx_hash,
        )

    def _apply_failure_classification(
        self,
        *,
        escrow: Escrow,
        payload_id: str,
        status: XamanPayloadStatus,
        tx_hash: str | None,
    ) -> None:
        if status == XamanPayloadStatus.DECLINED:
            escrow.failure_code = "signing_declined"
            escrow.failure_reason = _build_signing_failure_reason(
                payload_id=payload_id,
                signing_status=status,
                tx_hash=tx_hash,
            )
            return
        if status == XamanPayloadStatus.EXPIRED:
            escrow.failure_code = "signing_expired"
            escrow.failure_reason = _build_signing_failure_reason(
                payload_id=payload_id,
                signing_status=status,
                tx_hash=tx_hash,
            )
            return
        if status == XamanPayloadStatus.SIGNED and escrow.failure_code in {"signing_declined", "signing_expired"}:
            escrow.failure_code = None
            escrow.failure_reason = None

    def _append_audit_entry(
        self,
        *,
        actor_user_id: uuid.UUID,
        action: str,
        entity_id: str,
        outcome: str,
        details: dict[str, str | None],
    ) -> None:
        self.audit_logs.add(
            audit_log=AuditLog(
                actor_user_id=actor_user_id,
                action=action,
                entity_type="escrow",
                entity_id=entity_id,
                outcome=outcome,
                details_json=json.dumps(details, separators=(",", ":"), sort_keys=True, ensure_ascii=True),
            )
        )


def _status_to_outcome(status: XamanPayloadStatus) -> str:
    if status == XamanPayloadStatus.OPEN:
        return "pending"
    if status in {XamanPayloadStatus.DECLINED, XamanPayloadStatus.EXPIRED}:
        return "rejected"
    if status == XamanPayloadStatus.SIGNED:
        return "observed"
    return "unknown"


def _build_signing_failure_reason(*, payload_id: str, signing_status: XamanPayloadStatus, tx_hash: str | None) -> str:
    tx_hash_part = tx_hash or "none"
    return f"payload_id={payload_id};signing_status={signing_status.value};tx_hash={tx_hash_part}"
