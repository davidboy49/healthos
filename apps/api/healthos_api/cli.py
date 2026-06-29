import argparse

from sqlalchemy.orm import Session

from healthos_api.database import SessionLocal
from healthos_api.models import User
from healthos_api.security import hash_password


def create_admin(email: str, password: str) -> None:
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).one_or_none()
        if existing is not None:
            raise SystemExit(f"User already exists: {email}")
        db.add(User(email=email, password_hash=hash_password(password), is_admin=True))
        db.commit()
        print(f"Created admin user: {email}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal Health OS admin tools")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-admin")
    create.add_argument("--email", required=True)
    create.add_argument("--password", required=True)
    args = parser.parse_args()
    if args.command == "create-admin":
        create_admin(args.email, args.password)


if __name__ == "__main__":
    main()
