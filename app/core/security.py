from datetime import datetime, timedelta, timezone
from typing import Optional 
from fastapi import HTTPException

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

# password hashing 

pwd_context = CryptContext(schemes =["bcrypt"], deprecated="auto")

# defining hash password function 
def hash_password(password:str)->str:
    return pwd_context.hash(password)

#verify password 
def verify_password(plain_password:str, hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)

# craete JWT access token 
def create_access_token(data: dict, expires_delta:Optional[timedelta]=None)->str:
    #create a signed jwt access token with the given data and expiration time
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = (datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

# Decode JWT token 
def decode_access_token(token:str):
    #decode and validate a JWT token
    # this will return the payload to the function which we will use further for authorisation 

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    
    except JWTError:
        raise HTTPException(status_code = 401 , detail = "Invalid or expired token")
    