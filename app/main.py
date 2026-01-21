from fastapi import FastAPI, Response, status, HTTPException, Depends, Request#use ResponseModel to refine the output type
from fastapi.params import Body
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import Optional
from random import randrange
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from app.database import create_db_and_tables, get_session, lifespan
from sqlmodel import select
from app.database import post, SessionDep, User
from app.utils import hash
from app.routers import post as post_router, user as user_router, auth as auth_router, vote as vote_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan = lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router inclusion
app.include_router(post_router.router)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(vote_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World from Ann Arbor"}
