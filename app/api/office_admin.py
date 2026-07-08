from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.core.dependencies import get_current_super_admin

from app.models.user import User

from app.schemas.office_admin_schema import(OfficeAdminCreate,OfficeAdminResponse,OfficeAdminUpdate)

from app.services.office_admin_service import OfficeAdminService

router = APIRouter(prefix = "/office-admins", tags=["Office Admin Management"])


# Create Office Admin

@router.post(
    "",
    response_model=OfficeAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_office_admin(
    office_admin_data: OfficeAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    return OfficeAdminService.create_office_admin(
        db,
        office_admin_data,
    )


# ---------------------------------------------------------
# Get All Office Admins
# ---------------------------------------------------------
@router.get(
    "",
    response_model=list[OfficeAdminResponse],
)
def get_all_office_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    return OfficeAdminService.get_all_office_admins(db)


# ---------------------------------------------------------
# Get Office Admin by ID
# ---------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=OfficeAdminResponse,
)
def get_office_admin_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    return OfficeAdminService.get_office_admin_by_id(
        db,
        user_id,
    )


# ---------------------------------------------------------
# Update Office Admin
# ---------------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=OfficeAdminResponse,
)
def update_office_admin(
    user_id: int,
    office_admin_data: OfficeAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    return OfficeAdminService.update_office_admin(
        db,
        user_id,
        office_admin_data,
    )


# ---------------------------------------------------------
# Delete Office Admin
# ---------------------------------------------------------
@router.delete("/{user_id}")
def delete_office_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin),
):
    return OfficeAdminService.delete_office_admin(
        db,
        user_id,
    )
 

