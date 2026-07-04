import os
from dotenv import load_dotenv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

load_dotenv(PROJECT_ROOT / ".env")

from app.core.database import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password
from app.models.office import Office

db = SessionLocal()

try:
    #check if a superadmin already exists 
    existing_admin = ( db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first())

    if existing_admin:
        print("Super Admin already exists..")
    else:
        super_admin =User(
        first_name =  "Super",
        last_name = "Admin",
        email = os.getenv("SUPER_ADMIN_EMAIL"),
        password_hash = hash_password(os.getenv("SUPER_ADMIN_PASSWORD")),
        role = UserRole.SUPER_ADMIN,
        status = UserStatus.ACTIVE,
        office_id = None,
        must_change_password = False
        ) 

        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)

        print(f"Super Admin created successfully with ID {super_admin.user_id}")
except Exception as e:
        db.rollback()
        print(f"Error: {e}")
finally:
    db.close()
