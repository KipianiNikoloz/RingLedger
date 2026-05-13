from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.fighter_profile import FighterProfile
from app.repositories.fighter_profile_repository import FighterProfileRepository


@dataclass
class FighterProfileService:
    session: Session
    profiles: FighterProfileRepository = field(init=False)

    def __post_init__(self) -> None:
        self.profiles = FighterProfileRepository(session=self.session)

    def upsert_profile(self, *, user_id: uuid.UUID, display_name: str, xrpl_address: str) -> FighterProfile:
        existing_for_address = self.profiles.get_by_xrpl_address(xrpl_address=xrpl_address)
        if existing_for_address is not None and existing_for_address.user_id != user_id:
            raise ValueError("xrpl_address_already_exists")

        profile = self.profiles.get_for_user(user_id=user_id)
        if profile is None:
            profile = FighterProfile(user_id=user_id, display_name=display_name, xrpl_address=xrpl_address)
            self.profiles.add(profile=profile)
        else:
            profile.display_name = display_name
            profile.xrpl_address = xrpl_address

        self.session.flush()
        return profile
