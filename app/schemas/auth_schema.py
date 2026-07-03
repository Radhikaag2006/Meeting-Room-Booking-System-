# this is used to validate the login request and response 

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    # used for login requests 
    email : EmailStr
    password : str

class TokenResponse(BaseModel):
    # used after successful authentication it return the token 
    access_token : str
    token_type : str =  "bearer"

