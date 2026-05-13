from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import false, or_, select
from sqlalchemy.orm import Session

from app.models.bout import Bout
from app.models.enums import UserRole


@dataclass
class BoutRepository:
    session: Session

    def get(self, *, bout_id: uuid.UUID) -> Bout | None:
        return self.session.get(Bout, bout_id)

    def add(self, *, bout: Bout) -> None:
        self.session.add(bout)

    def list_visible_to_actor(self, *, user_id: uuid.UUID, role: UserRole) -> list[Bout]:
        statement = select(Bout).order_by(Bout.created_at.desc())
        if role == UserRole.PROMOTER:
            statement = statement.where(Bout.promoter_user_id == user_id)
        elif role == UserRole.FIGHTER:
            statement = statement.where(or_(Bout.fighter_a_user_id == user_id, Bout.fighter_b_user_id == user_id))
        elif role not in {UserRole.ADMIN, UserRole.MANAGEMENT}:
            statement = statement.where(false())
        return self.session.scalars(statement).all()

    def get_visible_to_actor(self, *, bout_id: uuid.UUID, user_id: uuid.UUID, role: UserRole) -> Bout | None:
        bout = self.get(bout_id=bout_id)
        if bout is None:
            return None
        if role in {UserRole.ADMIN, UserRole.MANAGEMENT}:
            return bout
        if role == UserRole.PROMOTER and bout.promoter_user_id == user_id:
            return bout
        if role == UserRole.FIGHTER and user_id in {bout.fighter_a_user_id, bout.fighter_b_user_id}:
            return bout
        return None
