from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
)

from app.core.security import hash_password


class EmployeeService:

    # ---------------------------------------------------------
    # Create Employee
    # ---------------------------------------------------------
    @staticmethod
    def create_employee(
        db: Session,
        employee_data: EmployeeCreate,
        current_user: User,
    ):

        # Check duplicate email
        if UserRepository.email_exists(db, employee_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists."
            )

        employee = User(
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            password_hash=hash_password(employee_data.password),
            office_id=current_user.office_id,
            role=UserRole.EMPLOYEE,
        )

        return UserRepository.create_user(db, employee)

    # ---------------------------------------------------------
    # Get All Employees
    # ---------------------------------------------------------
    @staticmethod
    def get_all_employees(
        db: Session,
        current_user: User,
    ):

        return UserRepository.get_employees_by_office(
            db,
            current_user.office_id,
        )

    # ---------------------------------------------------------
    # Get Employee By ID
    # ---------------------------------------------------------
    @staticmethod
    def get_employee_by_id(
        db: Session,
        user_id: int,
        current_user: User,
    ):

        employee = UserRepository.get_employee_by_id(
            db,
            user_id,
            current_user.office_id,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found."
            )

        return employee

    # ---------------------------------------------------------
    # Update Employee
    # ---------------------------------------------------------
    @staticmethod
    def update_employee(
        db: Session,
        user_id: int,
        employee_data: EmployeeUpdate,
        current_user: User,
    ):

        employee = EmployeeService.get_employee_by_id(
            db,
            user_id,
            current_user,
        )

        # Email uniqueness check
        if (
            employee_data.email is not None
            and employee_data.email != employee.email
        ):

            if UserRepository.email_exists(
                db,
                employee_data.email,
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists."
                )

            employee.email = employee_data.email

        if employee_data.first_name is not None:
            employee.first_name = employee_data.first_name

        if employee_data.last_name is not None:
            employee.last_name = employee_data.last_name

        if employee_data.status is not None:
            employee.status = employee_data.status

        return UserRepository.update_user(
            db,
            employee,
        )

    # ---------------------------------------------------------
    # Delete Employee
    # ---------------------------------------------------------
    @staticmethod
    def delete_employee(
        db: Session,
        user_id: int,
        current_user: User,
    ):

        employee = EmployeeService.get_employee_by_id(
            db,
            user_id,
            current_user,
        )

        UserRepository.delete_user(
            db,
            employee,
        )

        return {
            "message": "Employee deleted successfully."
        }