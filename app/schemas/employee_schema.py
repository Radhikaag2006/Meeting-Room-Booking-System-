from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.user import UserStatus

class EmployeeCreate(BaseModel):

    first_name : str
    last_name : str
    email:EmailStr
    password : str

class EmployeeUpdate(BaseModel):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    email : Optional[str] = None
    status : Optional[UserStatus]=None

class EmployeeResponse(BaseModel):
    user_id : int
    first_name : str
    last_name : str
    email : EmailStr
    office_id : int
    status : UserStatus

    model_config = ConfigDict(from_attributes=  True)