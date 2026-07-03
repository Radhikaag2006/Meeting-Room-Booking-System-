from app.core.database import SessionLocal 
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password
from dotenv import load_dotenv
import os

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
        must_chnage_password = False
        ) 

        db.add(super_admin)
        db.commit()

        print("Super Admin Created successfully")

finally:
    db.close()
