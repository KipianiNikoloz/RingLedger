from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.bout import Bout


@dataclass
class BoutRepository:
    session: Session

    def get(self, *, bout_id: uuid.UUID) -> Bout | None:
        return self.session.get(Bout, bout_id)

    def add(self, *, bout: Bout) -> None:
        self.session.add(bout)
