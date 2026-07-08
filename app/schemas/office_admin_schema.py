from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.user import UserStatus

class OfficeAdminCreate(BaseModel):
    first_name : str
    last_name : str
    email : EmailStr
    password:str
    office_id:int

class OfficeAdminUpdate(BaseModel):
    first_name : Optional[str]= None
    last_name : Optional[str] = None
    email : Optional[EmailStr] = None
    status : Optional[UserStatus] = None

class OfficeAdminResponse(BaseModel):
    user_id :int
    first_name : str
    last_name : str
    email : EmailStr
    office_id : int
    status : UserStatus

    model_config = ConfigDict(from_attributes = True)