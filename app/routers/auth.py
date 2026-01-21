from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import SessionDep
from app.database import User
from app.database import Token
from app.utils import verify
from app.oauth2 import create_access_token

router = APIRouter(
    prefix = "/auth",
    tags = ["authentication"],
)

@router.post("/login", response_model=Token)
def login(session: SessionDep, user_credentials: OAuth2PasswordRequestForm = Depends()):
    #user_credentials.password
    #check if the user exists
    user = session.exec(select(User).where(User.email == user_credentials.username)).first() #OAuth2PasswordRequestForm uses 'username' field, not 'email'
    if not user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid Credentials")
    #check if the password is correct
    #checking the hash password
    #user.password is the hashed password
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Invalid Credentials")
    access_token = create_access_token(data = {"user_id": user.id, "email": user.email})
    #we can put whatever we want in the data, it will be encoded in the token
    return {"access_token": access_token, "token_type": "bearer"}