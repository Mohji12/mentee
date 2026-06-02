"""Create a new admin account in the database."""

import argparse
import sys

from app.core.password import hash_password, validate_password
from app.db.database import SessionLocal
from app.db.models.admin import Admin


def create_admin(
    admin_id: str,
    password: str,
    admin_name: str,
    admin_email: str,
    admin_department: str = "Administration",
    admin_campus: str = "Jain University",
    admin_phoneno: str = "9999999999",
) -> None:
    validate_password(password)
    admin_id = admin_id.strip().upper()
    if len(admin_id) != 10:
        print(f"Error: admin_id must be exactly 10 characters (got {len(admin_id)}).", file=sys.stderr)
        sys.exit(1)
    admin_email = admin_email.strip().lower()

    db = SessionLocal()
    try:
        if db.query(Admin).filter(Admin.admin_id == admin_id).first():
            print(f"Error: admin_id '{admin_id}' already exists.", file=sys.stderr)
            sys.exit(1)
        if db.query(Admin).filter(Admin.admin_email == admin_email).first():
            print(f"Error: email '{admin_email}' already exists.", file=sys.stderr)
            sys.exit(1)

        admin = Admin(
            admin_id=admin_id,
            admin_name=admin_name,
            admin_department=admin_department,
            admin_campus=admin_campus,
            admin_email=admin_email,
            admin_phoneno=admin_phoneno,
            admin_password=hash_password(password),
        )
        db.add(admin)
        db.commit()
        print("Admin created successfully.")
        print(f"  Admin ID:  {admin_id}")
        print(f"  Name:      {admin_name}")
        print(f"  Email:     {admin_email}")
        print(f"  Password:  {password}")
        print("\nLog in at Admin Login using the Admin ID and password above.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new Mentee Tracker admin account")
    parser.add_argument("--id", default="MENTEEAD01", help="Admin login ID, 10 characters (default: MENTEEAD01)")
    parser.add_argument("--password", default="Admin@12345", help="Plain password (default: Admin@12345)")
    parser.add_argument("--name", default="Mentee Admin", help="Display name")
    parser.add_argument("--email", default="menteead01@jainuniversity.ac.in", help="Unique email")
    parser.add_argument("--department", default="Administration")
    parser.add_argument("--campus", default="Jain University")
    parser.add_argument("--phone", default="9999999999")
    args = parser.parse_args()

    create_admin(
        admin_id=args.id,
        password=args.password,
        admin_name=args.name,
        admin_email=args.email,
        admin_department=args.department,
        admin_campus=args.campus,
        admin_phoneno=args.phone,
    )
