# User Repository
# Performs all database operations related to the users table

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus


class UserRepository:

    # ---------------------------------------------------------
    # Get User By Email
    # ---------------------------------------------------------
    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
    ) -> Optional[User]:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    # ---------------------------------------------------------
    # Get User By ID
    # ---------------------------------------------------------
    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ):

        return (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

    # ---------------------------------------------------------
    # Create User
    # ---------------------------------------------------------
    @staticmethod
    def create_user(
        db: Session,
        user: User,
    ):

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # ---------------------------------------------------------
    # Check Email Exists
    # ---------------------------------------------------------
    @staticmethod
    def email_exists(
        db: Session,
        email: str,
    ) -> bool:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
            is not None
        )

    # ---------------------------------------------------------
    # Check Whether Office Already Has Admin
    # ---------------------------------------------------------
    @staticmethod
    def office_has_admin(
        db: Session,
        office_id: int,
    ) -> bool:

        return (
            db.query(User)
            .filter(
                User.office_id == office_id,
                User.role == UserRole.OFFICE_ADMIN,
            )
            .first()
            is not None
        )

    # ---------------------------------------------------------
    # Get All Office Admins
    # ---------------------------------------------------------
    @staticmethod
    def get_all_office_admins(
        db: Session,
    ):

        return (
            db.query(User)
            .filter(User.role == UserRole.OFFICE_ADMIN)
            .all()
        )

    # ---------------------------------------------------------
    # Get Employees Of An Office
    # ---------------------------------------------------------
    @staticmethod
    def get_employees_by_office(
        db: Session,
        office_id: int,
    ):

        return (
            db.query(User)
            .filter(
                User.role == UserRole.EMPLOYEE,
                User.office_id == office_id,
            )
            .all()
        )

    # ---------------------------------------------------------
    # Get Employee By ID
    # ---------------------------------------------------------
    @staticmethod
    def get_employee_by_id(
        db: Session,
        user_id: int,
        office_id: int,
    ):

        return (
            db.query(User)
            .filter(
                User.user_id == user_id,
                User.role == UserRole.EMPLOYEE,
                User.office_id == office_id,
            )
            .first()
        )

    # ---------------------------------------------------------
    # Update User
    # ---------------------------------------------------------
    @staticmethod
    def update_user(
        db: Session,
        user: User,
    ):

        db.commit()
        db.refresh(user)

        return user

    # ---------------------------------------------------------
    # Delete User
    # ---------------------------------------------------------
    @staticmethod
    def delete_user(
        db: Session,
        user: User,
    ):

        db.delete(user)
        db.commit()

    #  this function will be required during the booking
    @staticmethod
    def get_user_by_ids(db:Session, user_ids: list[int]):
        return(db.query(User).filter(User.user_id.in_(user_ids)).all())

    # ---------------------------------------------------------
    # Get Active Colleagues Of An Office (excludes the caller) -
    # used by the employee-facing attendee picker
    # ---------------------------------------------------------
    @staticmethod
    def get_active_colleagues(
        db: Session,
        office_id: int,
        exclude_user_id: int,
    ):

        return (
            db.query(User)
            .filter(
                User.role == UserRole.EMPLOYEE,
                User.office_id == office_id,
                User.status == UserStatus.ACTIVE,
                User.user_id != exclude_user_id,
            )
            .all()
        )

