from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fighter_profile import FighterProfile


@dataclass
class FighterProfileRepository:
    session: Session

    def get_for_user(self, *, user_id: uuid.UUID) -> FighterProfile | None:
        return self.session.scalar(select(FighterProfile).where(FighterProfile.user_id == user_id))

    def get_by_xrpl_address(self, *, xrpl_address: str) -> FighterProfile | None:
        return self.session.scalar(select(FighterProfile).where(FighterProfile.xrpl_address == xrpl_address))

    def add(self, *, profile: FighterProfile) -> None:
        self.session.add(profile)
