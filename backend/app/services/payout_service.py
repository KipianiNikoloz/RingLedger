from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.bout import Bout
from app.models.enums import BoutStatus, BoutWinner, EscrowKind, EscrowStatus
from app.models.escrow import Escrow
from app.services.xrpl_escrow_service import (
    EscrowPayoutAction,
    EscrowPayoutConfirmation,
    XrplEscrowService,
    XrplEscrowValidationError,
)

_EXPECTED_ESCROW_KINDS = {EscrowKind.SHOW_A, EscrowKind.SHOW_B, EscrowKind.BONUS_A, EscrowKind.BONUS_B}


@dataclass
class PayoutService:
    session: Session
    xrpl_service: XrplEscrowService = field(default_factory=XrplEscrowService)

    def enter_bout_result(
        self,
        *,
        bout_id: uuid.UUID,
        winner: BoutWinner,
        actor_user_id: uuid.UUID,
    ) -> Bout:
        bout = self.session.get(Bout, bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        if bout.status != BoutStatus.ESCROWS_CREATED:
            raise ValueError("bout_not_in_escrows_created_state")

        bout.winner = winner
        bout.status = BoutStatus.RESULT_ENTERED
        self._append_audit_entry(
            actor_user_id=actor_user_id,
            action="bout_result_enter",
            entity_type="bout",
            entity_id=str(bout.id),
            outcome="success",
            details={"winner": winner.value, "status": bout.status.value},
        )
        return bout

    def prepare_payout_payloads(self, *, bout_id: uuid.UUID) -> tuple[Bout, list[dict[str, Any]]]:
        bout = self.session.get(Bout, bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        if bout.status not in {BoutStatus.RESULT_ENTERED, BoutStatus.PAYOUTS_IN_PROGRESS}:
            raise ValueError("bout_not_preparable_for_payout")
        if bout.winner is None:
            raise ValueError("bout_winner_not_set")

        escrows_by_kind = self._load_escrows_by_kind(bout_id=bout_id)
        winner_bonus_kind, loser_bonus_kind = _resolve_bonus_kinds(winner=bout.winner)

        payout_plan: list[tuple[EscrowKind, EscrowPayoutAction, str | None]] = [
            (EscrowKind.SHOW_A, EscrowPayoutAction.FINISH, None),
            (EscrowKind.SHOW_B, EscrowPayoutAction.FINISH, None),
            (
                winner_bonus_kind,
                EscrowPayoutAction.FINISH,
                _required_fulfillment_hex(escrows_by_kind[winner_bonus_kind]),
            ),
            (loser_bonus_kind, EscrowPayoutAction.CANCEL, None),
        ]

        items: list[dict[str, Any]] = []
        for escrow_kind, action, fulfillment_hex in payout_plan:
            escrow = escrows_by_kind[escrow_kind]
            if escrow.status == EscrowStatus.CREATED:
                if action == EscrowPayoutAction.FINISH:
                    unsigned_tx = self.xrpl_service.build_escrow_finish_tx(
                        escrow=escrow, fulfillment_hex=fulfillment_hex
                    )
                else:
                    unsigned_tx = self.xrpl_service.build_escrow_cancel_tx(escrow)
                items.append(
                    {
                        "escrow_id": str(escrow.id),
                        "escrow_kind": escrow.kind,
                        "action": action.value,
                        "unsigned_tx": unsigned_tx,
                    }
                )
                continue

            if action == EscrowPayoutAction.FINISH and escrow.status == EscrowStatus.FINISHED:
                continue
            if action == EscrowPayoutAction.CANCEL and escrow.status == EscrowStatus.CANCELLED:
                continue
            raise ValueError("escrow_not_preparable_for_payout")

        return bout, items

    def confirm_payout(
        self,
        *,
        bout_id: uuid.UUID,
        escrow_kind: EscrowKind,
        confirmation: EscrowPayoutConfirmation,
    ) -> tuple[Bout, Escrow]:
        bout = self.session.get(Bout, bout_id)
        if bout is None:
            raise ValueError("bout_not_found")
        if bout.status not in {BoutStatus.RESULT_ENTERED, BoutStatus.PAYOUTS_IN_PROGRESS}:
            raise ValueError("bout_not_in_payout_state")
        if bout.winner is None:
            raise ValueError("bout_winner_not_set")

        escrow = self.session.scalar(
            select(Escrow).where(
                Escrow.bout_id == bout_id,
                Escrow.kind == escrow_kind,
            )
        )
        if escrow is None:
            raise ValueError("escrow_not_found")
        if escrow.status != EscrowStatus.CREATED:
            raise ValueError("escrow_not_created")

        expected_action, expected_fulfillment = self._expected_action_for_escrow(bout_winner=bout.winner, escrow=escrow)

        try:
            self.xrpl_service.validate_payout_confirmation(
                escrow=escrow,
                confirmation=confirmation,
                expected_action=expected_action,
                expected_fulfillment_hex=expected_fulfillment,
            )
        except XrplEscrowValidationError as exc:
            escrow.failure_code = "invalid_confirmation"
            escrow.failure_reason = str(exc)
            self._append_audit_entry(
                actor_user_id=None,
                action="escrow_payout_confirm",
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

        if expected_action == EscrowPayoutAction.FINISH:
            escrow.status = EscrowStatus.FINISHED
        else:
            escrow.status = EscrowStatus.CANCELLED
        escrow.close_tx_hash = confirmation.tx_hash
        escrow.failure_code = None
        escrow.failure_reason = None

        if bout.status == BoutStatus.RESULT_ENTERED:
            bout.status = BoutStatus.PAYOUTS_IN_PROGRESS
        self._append_audit_entry(
            actor_user_id=None,
            action="escrow_payout_confirm",
            entity_type="escrow",
            entity_id=str(escrow.id),
            outcome="success",
            details={
                "escrow_kind": escrow.kind.value,
                "status": escrow.status.value,
                "tx_hash": confirmation.tx_hash,
                "bout_status": bout.status.value,
            },
        )

        escrows_by_kind = self._load_escrows_by_kind(bout_id=bout_id)
        if _can_close_bout(winner=bout.winner, escrows_by_kind=escrows_by_kind):
            bout.status = BoutStatus.CLOSED
            self._append_audit_entry(
                actor_user_id=None,
                action="bout_closed",
                entity_type="bout",
                entity_id=str(bout.id),
                outcome="success",
                details={"status": bout.status.value},
            )

        return bout, escrow

    def _expected_action_for_escrow(
        self,
        *,
        bout_winner: BoutWinner,
        escrow: Escrow,
    ) -> tuple[EscrowPayoutAction, str | None]:
        winner_bonus_kind, loser_bonus_kind = _resolve_bonus_kinds(winner=bout_winner)
        if escrow.kind in {EscrowKind.SHOW_A, EscrowKind.SHOW_B}:
            return EscrowPayoutAction.FINISH, None
        if escrow.kind == winner_bonus_kind:
            return EscrowPayoutAction.FINISH, _required_fulfillment_hex(escrow)
        if escrow.kind == loser_bonus_kind:
            return EscrowPayoutAction.CANCEL, None
        raise ValueError("escrow_kind_not_supported")

    def _load_escrows_by_kind(self, *, bout_id: uuid.UUID) -> dict[EscrowKind, Escrow]:
        escrows = self.session.scalars(select(Escrow).where(Escrow.bout_id == bout_id)).all()
        escrows_by_kind = {item.kind: item for item in escrows}
        if set(escrows_by_kind) != _EXPECTED_ESCROW_KINDS:
            raise ValueError("bout_escrow_set_invalid")
        return escrows_by_kind

    def _append_audit_entry(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action: str,
        entity_type: str,
        entity_id: str,
        outcome: str,
        details: dict[str, Any],
    ) -> None:
        self.session.add(
            AuditLog(
                actor_user_id=actor_user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                outcome=outcome,
                details_json=json.dumps(details, separators=(",", ":"), sort_keys=True, ensure_ascii=True),
            )
        )


def _resolve_bonus_kinds(*, winner: BoutWinner) -> tuple[EscrowKind, EscrowKind]:
    if winner == BoutWinner.A:
        return EscrowKind.BONUS_A, EscrowKind.BONUS_B
    return EscrowKind.BONUS_B, EscrowKind.BONUS_A


def _required_fulfillment_hex(escrow: Escrow) -> str:
    if not escrow.encrypted_preimage_hex:
        raise ValueError("winner_bonus_fulfillment_missing")
    return escrow.encrypted_preimage_hex


def _can_close_bout(*, winner: BoutWinner, escrows_by_kind: dict[EscrowKind, Escrow]) -> bool:
    winner_bonus_kind, _ = _resolve_bonus_kinds(winner=winner)
    return (
        escrows_by_kind[EscrowKind.SHOW_A].status == EscrowStatus.FINISHED
        and escrows_by_kind[EscrowKind.SHOW_B].status == EscrowStatus.FINISHED
        and escrows_by_kind[winner_bonus_kind].status == EscrowStatus.FINISHED
    )
