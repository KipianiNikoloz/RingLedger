from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EscrowKind
from app.models.escrow import Escrow


@dataclass
class EscrowRepository:
    session: Session

    def add_many(self, *, escrows: list[Escrow]) -> None:
        self.session.add_all(escrows)

    def list_for_bout(self, *, bout_id: uuid.UUID) -> list[Escrow]:
        return self.session.scalars(select(Escrow).where(Escrow.bout_id == bout_id)).all()

    def get_for_bout_kind(self, *, bout_id: uuid.UUID, escrow_kind: EscrowKind) -> Escrow | None:
        return self.session.scalar(
            select(Escrow).where(
                Escrow.bout_id == bout_id,
                Escrow.kind == escrow_kind,
            )
        )
