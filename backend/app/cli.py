from __future__ import annotations

import argparse
import getpass
from pathlib import Path

from app.db.session import SessionLocal
from app.services.auth_service import AuthService


def bootstrap_admin(*, email: str, password: str) -> tuple[str, bool]:
    with SessionLocal() as session:
        user, created = AuthService(session).bootstrap_first_admin(email=email, password=password)
        session.commit()
        return str(user.id), created


def main() -> int:
    parser = argparse.ArgumentParser(prog="ringledger")
    subparsers = parser.add_subparsers(dest="command", required=True)
    bootstrap = subparsers.add_parser("bootstrap-admin", help="Create the first administrator")
    bootstrap.add_argument("--email", required=True)
    bootstrap.add_argument("--password-file", type=Path)
    args = parser.parse_args()

    if args.password_file is not None:
        password = args.password_file.read_text(encoding="utf-8").rstrip("\r\n")
    else:
        password = getpass.getpass("Admin password: ")
    if len(password) < 8:
        parser.error("password must contain at least 8 characters")

    user_id, created = bootstrap_admin(email=args.email, password=password)
    outcome = "created" if created else "already exists"
    print(f"Admin {args.email.strip().lower()} ({user_id}) {outcome}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
