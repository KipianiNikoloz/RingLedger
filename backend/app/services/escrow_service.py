from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.bout import Bout
from app.models.enums import BoutStatus, EscrowKind, EscrowStatus
from app.models.escrow import Escrow
from app.services.xrpl_escrow_service import EscrowCreateConfirmation, XrplEscrowService, XrplEscrowValidationError

_ESCROW_KIND_ORDER = {
    EscrowKind.SHOW_A: 0,
    EscrowKind.SHOW_B: 1,
    EscrowKind.BONUS_A: 2,
    EscrowKind.BONUS_B: 3,
}
_EXPECTED_ESCROW_KINDS = set(_ESCROW_KIND_ORDER)


@dataclass
class EscrowService:
    session: Session
    xrpl_service: XrplEscrowService = field(default_factory=XrplEscrowService)

    def prepare_escrow_create_payloads(self, *, bout_id: uuid.UUID) -> tuple[Bout, list[dict[str, Any]]]:
        bout = self.session.get(Bout, bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        if bout.status not in {BoutStatus.DRAFT, BoutStatus.ESCROWS_CREATED}:
            raise ValueError("bout_not_preparable_for_escrow_create")

        escrows = self.session.scalars(select(Escrow).where(Escrow.bout_id == bout_id)).all()
        escrows.sort(key=lambda escrow: _ESCROW_KIND_ORDER[escrow.kind])
        if {escrow.kind for escrow in escrows} != _EXPECTED_ESCROW_KINDS:
            raise ValueError("bout_escrow_set_invalid")

        items: list[dict[str, Any]] = []
        for escrow in escrows:
            if escrow.status not in {EscrowStatus.PLANNED, EscrowStatus.CREATED}:
                raise ValueError("escrow_not_preparable_for_create")
            items.append(
                {
                    "escrow_id": str(escrow.id),
                    "escrow_kind": escrow.kind,
                    "unsigned_tx": self.xrpl_service.build_escrow_create_tx(escrow),
                }
            )
        return bout, items

    def confirm_escrow_create(
        self,
        *,
        bout_id: uuid.UUID,
        escrow_kind: EscrowKind,
        confirmation: EscrowCreateConfirmation,
    ) -> tuple[Bout, Escrow]:
        bout = self.session.get(Bout, bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        if bout.status != BoutStatus.DRAFT:
            raise ValueError("bout_not_in_draft_state")

        escrow = self.session.scalar(
            select(Escrow).where(
                Escrow.bout_id == bout_id,
                Escrow.kind == escrow_kind,
            )
        )
        if escrow is None:
            raise ValueError("escrow_not_found")
        if escrow.status != EscrowStatus.PLANNED:
            raise ValueError("escrow_not_planned")

        try:
            self.xrpl_service.validate_escrow_create_confirmation(escrow=escrow, confirmation=confirmation)
        except XrplEscrowValidationError as exc:
            escrow.failure_code = "invalid_confirmation"
            escrow.failure_reason = str(exc)
            self._append_audit_entry(
                action="escrow_create_confirm",
                entity_type="escrow",
                entity_id=str(escrow.id),
                outcome="rejected",
                details={
                    "reason": str(exc),
                    "escrow_kind": escrow.kind.value,
                    "tx_hash": confirmation.tx_hash,
                },
            )
            raise ValueError(str(exc)) from exc

        escrow.status = EscrowStatus.CREATED
        escrow.offer_sequence = confirmation.offer_sequence
        escrow.create_tx_hash = confirmation.tx_hash
        escrow.failure_code = None
        escrow.failure_reason = None
        self._append_audit_entry(
            action="escrow_create_confirm",
            entity_type="escrow",
            entity_id=str(escrow.id),
            outcome="success",
            details={
                "escrow_kind": escrow.kind.value,
                "tx_hash": confirmation.tx_hash,
                "offer_sequence": confirmation.offer_sequence,
            },
        )

        escrows = self.session.scalars(select(Escrow).where(Escrow.bout_id == bout_id)).all()
        if {item.kind for item in escrows} == _EXPECTED_ESCROW_KINDS and all(
            item.status == EscrowStatus.CREATED for item in escrows
        ):
            bout.status = BoutStatus.ESCROWS_CREATED
            self._append_audit_entry(
                action="bout_escrows_created",
                entity_type="bout",
                entity_id=str(bout.id),
                outcome="success",
                details={"status": bout.status.value},
            )

        return bout, escrow

    def _append_audit_entry(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        outcome: str,
        details: dict[str, Any],
    ) -> None:
        self.session.add(
            AuditLog(
                actor_user_id=None,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                outcome=outcome,
                details_json=json.dumps(details, separators=(",", ":"), sort_keys=True, ensure_ascii=True),
            )
        )
