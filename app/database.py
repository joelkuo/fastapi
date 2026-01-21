from datetime import datetime, UTC
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from app.config import settings
from pydantic import conint

Base = DeclarativeBase()# SQLModel classes (database tables)
class post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str = Field(default=None, index=True)
    published: bool | None = Field(default=True, index=True)
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    owner_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE")))
    
    owner: Optional["User"] = Relationship(back_populates="posts")

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str = Field(index=True) 
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    
    posts: list["post"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE")))
    post_id: int = Field(sa_column=Column(Integer, ForeignKey("posts.id", ondelete="CASCADE")))
    
    


# Pydantic models (API models)
class UserCreate(BaseModel):
    email: str
    password: str

class UserOutput(BaseModel):
    email: str
    id: int
    created_at: datetime | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    email: str | None = None

class VoteCreate(BaseModel):
    post_id: int
    dir: int = Field(ge=0, le=1)  # ✅ Use int, not conintt    

# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
# postgres_url = "postgresql://postgres:gzh960827@localhost:5432/fastapi"
postgres_url = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# connect_args = {"check_same_thread": False}
engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    DEPENDS FUNCTION - Request-Level Dependency Injection
    
    DIFFERENCE FROM LIFESPAN:
    - lifespan: Runs ONCE per app lifecycle (application-wide)
    - Depends: Runs for EVERY request (request-specific)
    
    WHAT THIS FUNCTION DOES:
    - Creates a NEW database session for EVERY request
    - Yields the session to the endpoint
    - Automatically closes the session after the request
    
    USE CASES:
    - Database sessions per request
    - User authentication per request
    - Request validation
    - Rate limiting per request
    
    PERFORMANCE IMPACT: HIGH - runs for every single request
    
    PARALLELIZATION ROLE:
    - Each request gets a fresh session (prevents data leakage)
    - Sessions can run on different connections from the pool
    - Enables multiple requests to execute database queries simultaneously
    - Think: lifespan creates the "parking garage" (connections), 
      this creates the "parking spots" (sessions) for each car (request)
    """
    with Session(engine) as session:
        yield session  # ✅ Provides session to endpoint, closes after request
# CONNINFO = "postgresql://postgres:gzh960827@localhost:5432/fastapi"
CONNINFO = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    LIFESPAN FUNCTION - Application Lifecycle Management
    
    DIFFERENCE FROM DEPENDS:
    - lifespan: Runs ONCE when app starts/stops (application-wide)
    - Depends: Runs for EVERY request (request-specific)
    
    WHAT THIS FUNCTION DOES:
    1. STARTUP (before any requests): Creates database pool, sets up tables
    2. RUNTIME: App handles requests (at the 'yield' point)
    3. SHUTDOWN (after all requests): Closes database pool, cleanup
    
    USE CASES:
    - Database connection pools (expensive to create/destroy)
    - Creating database tables (one-time setup)
    - Loading configuration files
    - Setting up external services
    - Cleanup operations
    
    PERFORMANCE IMPACT: ZERO - runs once, not per request
    
    PARALLELIZATION BENEFITS:
    - Creates 5 database connections in pool
    - Multiple requests can use different connections simultaneously
    - Enables true database query parallelization
    - Without this: all requests would wait in line for 1 connection
    """
    
    # ✅ STARTUP PHASE: Create resources once when app starts
    
    # CONNECTION POOL FOR PARALLELIZATION:
    # - min_size=1: Always have at least 1 connection ready
    # - max_size=5: Allow up to 5 concurrent database connections
    # - This enables 5 requests to run database queries simultaneously
    # - Without pooling: each request would create/destroy connections (slow)
    pool = ConnectionPool(CONNINFO, min_size=1, max_size=5, kwargs={"autocommit": True})
    app.state.pool = pool
    print("DB pool ready.")
    
    # Create database tables using SQLModel (one-time setup)
    create_db_and_tables()
    
    try:
        yield  # ✅ RUNTIME: App handles requests here
    finally:
        # ✅ SHUTDOWN PHASE: Cleanup when app stops
        pool.close()
        print("DB pool closed.")

# DEPENDENCY TYPE ANNOTATION
# This creates a reusable type that automatically injects a database session
# Every endpoint using SessionDep will get a fresh database session per request

# PARALLELIZATION EXPLANATION:
# - Multiple requests can use SessionDep simultaneously
# - Each gets a different session, potentially using different connections
# - This enables true parallelization: Request A on Connection 1, Request B on Connection 2
# - Without this pattern: all requests would share the same session (data corruption risk)
SessionDep = Annotated[Session, Depends(get_session)]
