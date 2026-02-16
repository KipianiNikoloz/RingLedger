from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    PROMOTER = "promoter"
    FIGHTER = "fighter"
    MANAGEMENT = "management"
    ADMIN = "admin"


class BoutStatus(StrEnum):
    DRAFT = "draft"
    READY_FOR_ESCROW = "ready_for_escrow"
    ESCROWS_CREATED = "escrows_created"
    RESULT_ENTERED = "result_entered"
    PAYOUTS_IN_PROGRESS = "payouts_in_progress"
    CLOSED = "closed"


class EscrowKind(StrEnum):
    SHOW_A = "show_a"
    SHOW_B = "show_b"
    BONUS_A = "bonus_a"
    BONUS_B = "bonus_b"


class EscrowStatus(StrEnum):
    PLANNED = "planned"
    CREATED = "created"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BoutWinner(StrEnum):
    A = "A"
    B = "B"

