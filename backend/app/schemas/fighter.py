from __future__ import annotations

from pydantic import BaseModel, Field

XRPL_CLASSIC_ADDRESS_PATTERN = r"^r[1-9A-HJ-NP-Za-km-z]{24,34}$"


class FighterProfileUpsertRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    xrpl_address: str = Field(min_length=25, max_length=35, pattern=XRPL_CLASSIC_ADDRESS_PATTERN)


class FighterProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    display_name: str
    xrpl_address: str
