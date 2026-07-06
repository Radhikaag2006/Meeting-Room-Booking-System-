from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db 
from app.core.dependencies import get_current_super_admin

from app.models.user import User

from app.schemas.office_schema import(OfficeCreate, OfficeResponse)
from app.services.office_service import OfficeService

router = APIRouter(prefix = "/offices", tags=["Office Mangement"])

@router.post("/", response_model = OfficeResponse, status_code = 201)
def create_office(office: OfficeCreate, db:Session = Depends(get_db), current_user :User = Depends(get_current_super_admin)
                  ):
    return OfficeService.create_office(db,office)

@router.get("/",response_model = list[OfficeResponse])
def get_all_offices(db:Session = Depends(get_db), current_user : User = Depends(get_current_super_admin)):
    return OfficeService.get_all_offices(db)

@router.get("/{office_id}", response_model = OfficeResponse)
def get_office(office_id : int, db:Session = Depends(get_db), current_user : User = Depends(get_current_super_admin)):
    return OfficeService.get_office_by_id(db, office_id)
    


