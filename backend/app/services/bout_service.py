from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.crypto_conditions import generate_preimage_hex, make_condition_hex, make_fulfillment_hex
from app.domain.time_rules import (
    compute_bonus_cancel_after,
    compute_finish_after,
    to_ripple_epoch,
)
from app.models.bout import Bout
from app.models.enums import EscrowKind, EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.user import User
from app.repositories.bout_repository import BoutRepository
from app.repositories.escrow_repository import EscrowRepository
from app.repositories.fighter_profile_repository import FighterProfileRepository


@dataclass
class BoutService:
    session: Session
    bouts: BoutRepository = field(init=False)
    escrows: EscrowRepository = field(init=False)
    fighter_profiles: FighterProfileRepository = field(init=False)

    def __post_init__(self) -> None:
        self.bouts = BoutRepository(session=self.session)
        self.escrows = EscrowRepository(session=self.session)
        self.fighter_profiles = FighterProfileRepository(session=self.session)

    def create_bout_draft_for_promoter(
        self,
        *,
        promoter_user_id: uuid.UUID,
        fighter_a_user_id: uuid.UUID,
        fighter_b_user_id: uuid.UUID,
        event_datetime_utc: datetime,
        promoter_owner_address: str,
        show_a_drops: int,
        show_b_drops: int,
        bonus_a_drops: int,
        bonus_b_drops: int,
    ) -> Bout:
        if fighter_a_user_id == fighter_b_user_id:
            raise ValueError("fighters_must_be_distinct")

        fighter_a = self.session.get(User, fighter_a_user_id)
        fighter_b = self.session.get(User, fighter_b_user_id)
        if fighter_a is None or fighter_b is None:
            raise ValueError("fighter_not_found")
        if fighter_a.role != UserRole.FIGHTER or fighter_b.role != UserRole.FIGHTER:
            raise ValueError("user_is_not_fighter")

        fighter_a_profile = self.fighter_profiles.get_for_user(user_id=fighter_a_user_id)
        fighter_b_profile = self.fighter_profiles.get_for_user(user_id=fighter_b_user_id)
        if fighter_a_profile is None or fighter_b_profile is None:
            raise ValueError("fighter_profile_required")

        return self.create_bout_draft(
            promoter_user_id=promoter_user_id,
            fighter_a_user_id=fighter_a_user_id,
            fighter_b_user_id=fighter_b_user_id,
            event_datetime_utc=event_datetime_utc,
            promoter_owner_address=promoter_owner_address,
            fighter_a_destination=fighter_a_profile.xrpl_address,
            fighter_b_destination=fighter_b_profile.xrpl_address,
            show_a_drops=show_a_drops,
            show_b_drops=show_b_drops,
            bonus_a_drops=bonus_a_drops,
            bonus_b_drops=bonus_b_drops,
        )

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
        self.bouts.add(bout=bout)
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
        self.escrows.add_many(escrows=escrows)
        self.session.flush()
        return bout
