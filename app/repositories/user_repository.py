# user to perform operations with tehdatabse 
from sqlalchemy.orm import Session 
from app.models.user import User,UserRole
from typing import Optional

class UserRepository:
    @staticmethod
    def get_user_by_email(db : Session, email:str)-> Optional[User]:
        # this function will return the user object if the user with the given email exists in the database 
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db:Session, user_id : int):
        # this func will fetch the user by it's PK
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod 
    def create_user(db:Session, user:User):
        # to add a new user to databse 
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod 
    def email_exists(db:Session, email:str)->bool:
        return db.query(User).filter(User.email==email).first() is not None
    
# This method will check whether there is already any admin in the office
    @staticmethod
    def office_has_admin(db:Session, office_id: int)->bool:
        return (db.query(User).filter(User.office_id == office_id, User.role == UserRole.OFFICE_ADMIN).first() is not None)
    
    # defining the get all office admins 
    @staticmethod
    def get_all_office_admins(db:Session):
        return (db.query(User).filter(User.role == UserRole.OFFICE_ADMIN).all())