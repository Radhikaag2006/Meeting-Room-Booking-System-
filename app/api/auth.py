from fastapi import APIRouter 
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.auth_schema import (LoginRequest, TokenResponse)
from app.services.auth_services  import AuthService
from app.core.dependencies import get_current_user
from app.schemas.user_schema import UserResponse
from app.models.user import User 
from app.core.dependencies import get_current_super_admin

router = APIRouter(prefix = "/auth", tags = ["Authenticatiom"])

@router.post("/login",response_model = TokenResponse)
def login(login_data : LoginRequest, db : Session = Depends(get_db)):
    return AuthService.login(db, login_data)

# endpoint to test whether we are geeting the decoded payload or not 
@router.get(
    "/me",
    response_model=UserResponse
)
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

# testing the get_current_super_admin
@router.get("/super-admin-test")
def super_admin_test(current_user : User = Depends(get_current_super_admin)):
    return {
        "message" : "Welcome super admin",
        "user" : current_user.email
    }