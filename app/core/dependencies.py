# this will help us to get the details of the current logged In user from the authorisation jwt tokens 

# extraction of jwt token from auth header 
# we will pass the extracted header  to thefunction 

#Oauth2PasswordBearer simply extracts the eyJhbGc... from  Bearer eyJhbGc...
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.core.security import decode_access_token

from app.repositories.user_repository import UserRepository
from app.models.user import User, UserStatus, UserRole

# Extracts JWT from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/auth/login")

async def get_current_user(token:str= Depends(oauth2_scheme), db:Session = Depends(get_db))->User:
   
   # Decode JWT
    payload = decode_access_token(token)
    # Extracting the user_id from the payload  
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token payload"
        )
    
    # Fetch the user from the databse 
    user = UserRepository.get_user_by_id(db,user_id)

    if user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, detail = "User does not exist"
        )
    
    #Check whether the account is active 
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "User account is inactive"
        )
    return user

# here we are returning the dictionary but we actually want a user object in order to ectract the name and other details in the API' endpoints 
# so we will convert this dictionary into user Object  

# Now checking whether the user is super admin or  not
async def get_current_super_admin(current_user : User= Depends(get_current_user))->User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN, 
            detail = "Only Super Admin can perform this action."
        )
    return current_user 

# checking whether someone if office admin or not 
async def get_current_office_admin(
        current_user: User = Depends(get_current_user)
)->User:
    

    if current_user.role != UserRole.OFFICE_ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
                    detail ="Only Office Admin can perform this action.")
    return current_user

# Checking whether someone is employee or not 
async def get_current_employee(
    current_user: User = Depends(get_current_user)
) -> User:

    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can access this resource."
        )

    return current_user