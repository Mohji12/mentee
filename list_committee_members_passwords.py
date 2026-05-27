"""
List all committee members and optionally set/reset their passwords to a known value.

Passwords in the database are hashed and cannot be retrieved. This script lets you:
1. List all committee members (ID, name, email, role).
2. Set all committee members' passwords to a new value and print that password next to each member.

Run from project root:
  python list_committee_members_passwords.py
  python list_committee_members_passwords.py --set-password "YourNewPassword"
  python list_committee_members_passwords.py --set-password "YourNewPassword" --export credentials.txt
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password, validate_password


def main():
    parser = argparse.ArgumentParser(
        description="List committee members and optionally set a common password for all"
    )
    parser.add_argument(
        "--set-password",
        metavar="PASSWORD",
        help="Set this password for ALL committee members (will overwrite existing). Password is then shown in the output.",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Write credentials to this file (e.g. credentials.txt or credentials.csv)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        members = (
            db.query(CommitteeMember)
            .order_by(CommitteeMember.role, CommitteeMember.id)
            .all()
        )

        if not members:
            print("No committee members found in the database.")
            return

        password_to_show = None
        if args.set_password:
            try:
                validate_password(args.set_password)
            except Exception as e:
                print(f"Password validation failed: {e}")
                sys.exit(1)
            hashed = hash_password(args.set_password)
            for m in members:
                m.password_hash = hashed
            db.commit()
            password_to_show = args.set_password
            print("All committee member passwords have been set to the new password.\n")

        # Build output lines
        lines = []
        header = "Login ID (Username)\tName\tEmail\tRole\tDepartment/Allocation\tPassword"
        lines.append(header)
        lines.append("-" * 80)

        for m in members:
            role = m.role or ""
            dept_info = ""
            if m.department:
                dept_info = m.department
            elif m.allocated_departments:
                dept_info = m.allocated_departments[:60] + ("..." if len(m.allocated_departments) > 60 else "")
            elif m.allocated_programs:
                dept_info = m.allocated_programs[:60] + ("..." if len(m.allocated_programs) > 60 else "")

            pwd_cell = password_to_show if password_to_show else "(stored as hash, use --set-password to set a new one)"
            line = "\t".join([
                str(m.id),
                str(m.name or ""),
                str(m.email or ""),
                role,
                dept_info.replace("\t", " "),
                pwd_cell,
            ])
            lines.append(line)

        text = "\n".join(lines)
        print(text)

        if args.export:
            with open(args.export, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"\nCredentials written to: {args.export}")

        if not password_to_show:
            print("\nNote: Passwords cannot be retrieved (they are hashed). Use --set-password 'YourPassword' to set a new password for all members and see it in the list.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
