from sqlmodel import Field, Session, SQLModel, create_engine, select

from typing import Annotated
from datetime import datetime, UTC

from fastapi import Depends, FastAPI, HTTPException, Query


# class Hero(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     age: int | None = Field(default=None, index=True)
#     secret_name: str

class post(SQLModel, table=True):
    #this is pydantic model
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str = Field(default=None, index=True)
    published: bool | None = Field(default=True, index=True)
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
postgres_url = "postgresql://postgres:gzh960827@localhost:5432/fastapi"

# connect_args = {"check_same_thread": False}
engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]