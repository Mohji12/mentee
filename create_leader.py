"""Create a new committee head (leader) in committee_members."""

import argparse
import sys

from app.core.password import hash_password, validate_password
from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember


def create_leader(
    leader_id: str,
    password: str,
    name: str,
    email: str,
) -> None:
    validate_password(password)
    leader_id = leader_id.strip()
    email = email.strip().lower()

    db = SessionLocal()
    try:
        existing = (
            db.query(CommitteeMember)
            .filter(CommitteeMember.id.ilike(leader_id))
            .first()
        )
        if existing:
            print(f"Error: leader id '{existing.id}' already exists.", file=sys.stderr)
            sys.exit(1)
        if db.query(CommitteeMember).filter(CommitteeMember.email == email).first():
            print(f"Error: email '{email}' already exists.", file=sys.stderr)
            sys.exit(1)

        member = CommitteeMember(
            id=leader_id,
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="leader",
            department=None,
            allocated_departments=None,
            allocated_programs=None,
        )
        db.add(member)
        db.commit()
        print("Leader created successfully.")
        print(f"  Leader ID:  {leader_id}")
        print(f"  Name:       {name}")
        print(f"  Email:      {email}")
        print(f"  Password:   {password}")
        print("\nLog in with Leader role using the ID and password above.")
        print("Route after login: /leader/{leader_id}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Mentee Tracker committee head (leader)")
    parser.add_argument("--id", default="LEADER0002", help="Login ID (default: LEADER0002)")
    parser.add_argument("--password", default="Leader@12345", help="Password (default: Leader@12345)")
    parser.add_argument("--name", default="Committee Head", help="Display name")
    parser.add_argument("--email", default="leader0002@jainuniversity.ac.in", help="Unique email")
    args = parser.parse_args()
    create_leader(args.id, args.password, args.name, args.email)
