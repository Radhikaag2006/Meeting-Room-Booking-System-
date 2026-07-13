from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.dependencies import get_current_office_admin, get_current_employee
from app.models.user import User

from app.core.database import get_db

from app.schemas.employee_schema import(EmployeeCreate, EmployeeUpdate, EmployeeResponse)

from app.services.employee_service import EmployeeService

router = APIRouter(prefix = "/employees", tags=["Employee Management"])

# CREATE EMPLOYEE
@router.post("",response_model = EmployeeResponse, status_code = status.HTTP_201_CREATED)

def create_employee(employee_data: EmployeeCreate, db: Session= Depends(get_db), current_user : User = Depends(get_current_office_admin)):
    return EmployeeService.create_employee(db, employee_data,current_user)

# GET ALL EMPLOYEES
@router.get("", response_model =  list[EmployeeResponse])
def get_all_employees(db:Session= Depends(get_db), current_user : User = Depends(get_current_office_admin)):
    return EmployeeService.get_all_employees(db, current_user)

# GET COLLEAGUES - employee-facing (attendee picker); must be declared
# before "/{user_id}" so it isn't swallowed by that route
@router.get("/colleagues", response_model = list[EmployeeResponse])
def get_colleagues(db:Session= Depends(get_db), current_user : User = Depends(get_current_employee)):
    return EmployeeService.get_colleagues(db, current_user)

# GET EMPLOYEE BY ID
@router.get("/{user_id}",response_model = EmployeeResponse)
def get_employee_by_id(user_id: int, db:Session=Depends(get_db), current_user : User = Depends(get_current_office_admin)):
    return EmployeeService.get_employee_by_id(db, user_id, current_user)

# UPDATE EMPLOYEE
@router.put("/{user_id}", response_model =EmployeeResponse)
def update_employee(user_id : int,
                    employee_data : EmployeeUpdate,
                    db: Session = Depends(get_db),
                    current_user : User = Depends(get_current_office_admin)):
    return EmployeeService.update_employee(db, user_id, employee_data, current_user)

# DELETE EMPLOYEE 
@router.delete("/{user_id}")
def delete_employee(
    user_id : int, db:Session= Depends(get_db),current_user : User = Depends(get_current_office_admin)):
    return EmployeeService.delete_employee(db, user_id, current_user)


