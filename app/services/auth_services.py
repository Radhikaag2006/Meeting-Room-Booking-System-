from sqlalchemy.orm import Session
from fastapi import HTTPException , status

from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest
from app.core.security import(verify_password,create_access_token)

class AuthService:
    @staticmethod
    def login(db:Session, login_data : LoginRequest):

        # check if the user exists in the table or not 
        user = UserRepository.get_user_by_email(db,login_data.email)
        if user is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                      detail="User does not exist." )
        # verify password 
        if not verify_password(login_data.password,user.password_hash):
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect Password")
        
        # CHECK USER STATUS 
        if user.status.value != "ACTIVE":
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "User account is inactive")
        
        # Generate JWT 
        access_token = create_access_token(
            data = {
                "user_id":user.user_id,
                "role":user.role.value,
                "office_id":user.office_id
            }
        )

        # Return Token 
        return {
            "access_token ": access_token,
            "token_type": "bearer"
        }
