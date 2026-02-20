from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.crypto_conditions import generate_preimage_hex, make_condition_hex, make_fulfillment_hex
from app.domain.time_rules import (
    compute_bonus_cancel_after,
    compute_finish_after,
    to_ripple_epoch,
)
from app.models.bout import Bout
from app.models.enums import EscrowKind, EscrowStatus
from app.models.escrow import Escrow


@dataclass
class BoutService:
    session: Session

    def create_bout_draft(
        self,
        *,
        promoter_user_id: uuid.UUID,
        fighter_a_user_id: uuid.UUID,
        fighter_b_user_id: uuid.UUID,
        event_datetime_utc: datetime,
        promoter_owner_address: str,
        fighter_a_destination: str,
        fighter_b_destination: str,
        show_a_drops: int,
        show_b_drops: int,
        bonus_a_drops: int,
        bonus_b_drops: int,
    ) -> Bout:
        finish_after = compute_finish_after(event_datetime_utc)
        cancel_after = compute_bonus_cancel_after(event_datetime_utc)
        finish_after_ripple = to_ripple_epoch(finish_after)
        cancel_after_ripple = to_ripple_epoch(cancel_after)
        bonus_a_preimage = generate_preimage_hex()
        bonus_b_preimage = generate_preimage_hex()
        bonus_a_fulfillment = make_fulfillment_hex(bonus_a_preimage)
        bonus_b_fulfillment = make_fulfillment_hex(bonus_b_preimage)
        bonus_a_condition = make_condition_hex(bonus_a_fulfillment)
        bonus_b_condition = make_condition_hex(bonus_b_fulfillment)

        bout = Bout(
            promoter_user_id=promoter_user_id,
            fighter_a_user_id=fighter_a_user_id,
            fighter_b_user_id=fighter_b_user_id,
            event_datetime_utc=event_datetime_utc,
            finish_after_utc=finish_after,
            cancel_after_utc=cancel_after,
            show_a_drops=show_a_drops,
            show_b_drops=show_b_drops,
            bonus_a_drops=bonus_a_drops,
            bonus_b_drops=bonus_b_drops,
        )
        self.session.add(bout)
        self.session.flush()

        escrows = [
            Escrow(
                bout_id=bout.id,
                kind=EscrowKind.SHOW_A,
                status=EscrowStatus.PLANNED,
                owner_address=promoter_owner_address,
                destination_address=fighter_a_destination,
                amount_drops=show_a_drops,
                finish_after_ripple=finish_after_ripple,
                cancel_after_ripple=None,
            ),
            Escrow(
                bout_id=bout.id,
                kind=EscrowKind.SHOW_B,
                status=EscrowStatus.PLANNED,
                owner_address=promoter_owner_address,
                destination_address=fighter_b_destination,
                amount_drops=show_b_drops,
                finish_after_ripple=finish_after_ripple,
                cancel_after_ripple=None,
            ),
            Escrow(
                bout_id=bout.id,
                kind=EscrowKind.BONUS_A,
                status=EscrowStatus.PLANNED,
                owner_address=promoter_owner_address,
                destination_address=fighter_a_destination,
                amount_drops=bonus_a_drops,
                finish_after_ripple=finish_after_ripple,
                cancel_after_ripple=cancel_after_ripple,
                condition_hex=bonus_a_condition,
                encrypted_preimage_hex=bonus_a_fulfillment,
            ),
            Escrow(
                bout_id=bout.id,
                kind=EscrowKind.BONUS_B,
                status=EscrowStatus.PLANNED,
                owner_address=promoter_owner_address,
                destination_address=fighter_b_destination,
                amount_drops=bonus_b_drops,
                finish_after_ripple=finish_after_ripple,
                cancel_after_ripple=cancel_after_ripple,
                condition_hex=bonus_b_condition,
                encrypted_preimage_hex=bonus_b_fulfillment,
            ),
        ]
        self.session.add_all(escrows)
        self.session.commit()
        self.session.refresh(bout)
        return bout
