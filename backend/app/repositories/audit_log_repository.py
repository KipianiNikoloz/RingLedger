from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


@dataclass
class AuditLogRepository:
    session: Session

    def add(self, *, audit_log: AuditLog) -> None:
        self.session.add(audit_log)
