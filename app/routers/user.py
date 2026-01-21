from fastapi import status, HTTPException, APIRouter
from sqlmodel import Session, select
from app.database import User, SessionDep, UserCreate, UserOutput
from app.utils import hash, verify
from datetime import datetime, UTC
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserOutput(BaseModel):
    email: str
    id: int
    created_at: datetime | None = None 

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOutput)
def create_user(user_data: UserCreate, session: SessionDep):
    # Hash the password
    hashed_password = hash(user_data.password)
    
    # Create User object with hashed password
    db_user = User(
        email=user_data.email,
        password=hashed_password,  
        created_at=datetime.now(UTC)
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/{id}", response_model = UserOutput)
def get_user(id: int, session: SessionDep):
    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"User with id: {id} was not found")
    return db_user