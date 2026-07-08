from typing import Optional 
from pydantic import BaseModel, EmailStr , ConfigDict
from app.models.user import UserRole, UserStatus

class UserCreate(BaseModel):
    # request schemawhen creating a new user 
    first_name : str
    last_name : str
    email : EmailStr
    password : str
    role : UserRole
    office_id : Optional[int] = None

# this is the schema returned in form of response when the user is successfully created 
class UserResponse(BaseModel):

    # Response Schema Returned after fetching or creating a user 

    user_id : int
    first_name : str
    last_name :  str
    email : EmailStr
    role : UserRole
    status : UserStatus
    office_id : Optional[int]

    model_config = ConfigDict(from_attributes=True)

# this schema will be used when we willupdate the user 
class UserUpdate(BaseModel):
    # reuest schema when we want to modify user details 
    first_name : Optional[str]= None
    last_name : Optional[str] = None
    email : Optional[EmailStr] = None
    role : Optional[UserRole] = None
    status : Optional[UserStatus] = None
    office_id: Optional[int] = None
    