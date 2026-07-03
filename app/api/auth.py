from fastapi import APIRouter 
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.auth_schema import (LoginRequest, TokenResponse)
from app.services.auth_services  import AuthService

router = APIRouter(prefix = "/auth", tags = ["Authenticatiom"])

@router.post("/login",reposnse_model = TokenResponse)
def login(login_data : LoginRequest, db : Session = Depends(get_db)):
    return AuthService.login(db, login_data)
