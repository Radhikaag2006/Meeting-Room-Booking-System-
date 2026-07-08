from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.office_repository import OfficeRepository 

from app.schemas.office_admin_schema import (OfficeAdminCreate, OfficeAdminUpdate)

from app.core.security import hash_password

class OfficeAdminService:

    #creating an office admin 
    @staticmethod
    def create_office_admin(db:Session, office_admin_data: OfficeAdminCreate):

        # checking whether office already exists 
        if not OfficeRepository.office_exists(db, office_admin_data.office_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Office does not exist."
            )
        
        #Check whether offuce already has am office admin
        if UserRepository.office_has_admin(db, office_admin_data.office_id):
            raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                          detail = "Office already has an office admin.")
            
        
        # cHeck duplicate emial 
        if UserRepository.email_exists(db, office_admin_data.email):
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Email already exists.")
        
        office_admin = User(
            first_name = office_admin_data.first_name,
            last_name = office_admin_data.last_name,
            email = office_admin_data.email,
            password_hash = hash_password(office_admin_data.password),
            office_id = office_admin_data.office_id,
            role = UserRole.OFFICE_ADMIN
        )

        return UserRepository.create_user(db, office_admin)
    
    # Get all office admins 
    @staticmethod 
    def get_all_office_admins(db:Session):
        return(db.query(User).filter(User.role == UserRole.OFFICE_ADMIN).all())

    # Get Office Admin by ID 
    @staticmethod
    def get_office_admin_by_id(db:Session, user_id : int):

        office_admin = UserRepository.get_user_by_id(db, user_id)

        if(office_admin is None or office_admin.role !=  UserRole.OFFICE_ADMIN):
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Office Admin not found.")
        return  office_admin

    # Update Office Admin
    @staticmethod
    def update_office_admin(db:Session, user_id: int, office_admin_data : OfficeAdminUpdate):
        office_admin = UserRepository.get_user_by_id(db, user_id)

        if(office_admin is None or office_admin.role != UserRole.OFFICE_ADMIN):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                                detail = "Office  Admin not found")
        
        # Email uniquemness check 
        if(office_admin_data.email is not None and office_admin_data.email != office_admin.email):
            if UserRepository.email_exists(
                    db,
                    office_admin_data.email,
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already exists.",
                    )

            office_admin.email = office_admin_data.email

        if office_admin_data.first_name is not None:
            office_admin.first_name = (office_admin_data.first_name)
        
        if office_admin_data.last_name is not None:
            office_admin.last_name =  (office_admin_data.last_name)

        if office_admin_data.status is not None:
            office_admin.status=(
                office_admin_data.status)
        
        db.commit()
        db.refresh(office_admin)

        return office_admin

    # Delete Office Admin
    @staticmethod
    def delete_office_admin(
        db: Session,
        user_id: int,
    ):

        office_admin = UserRepository.get_user_by_id(
            db,
            user_id,
        )

        if (
            office_admin is None
            or office_admin.role != UserRole.OFFICE_ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Office Admin not found.",
            )

        db.delete(office_admin)
        db.commit()

        return {
            "message": "Office Admin deleted successfully."
        }
                                
