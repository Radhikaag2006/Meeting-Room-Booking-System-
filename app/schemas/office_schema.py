# this file contains the classes for office 

from typing import Optional
from pydantic import BaseModel, ConfigDict

class OfficeCreate(BaseModel):
    office_name : str
    address :  str
    city : str
    state: str
    country : str

class OfficeUpdate(BaseModel):
    office_name : Optional[str] = None
    address : Optional[str] = None
    city : Optional[str] = None
    state : Optional[str] = None
    country : Optional[str] = None

class OfficeResponse(BaseModel):
    office_id : int
    office_name : str
    address : str
    city : str
    state : str
    country : str

    model_config = ConfigDict(from_attributes = True)