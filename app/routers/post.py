from fastapi import Response, status, HTTPException, APIRouter, Depends#use ResponseModel to refine the output type, APIRouter
from pydantic import BaseModel
from sqlmodel import Boolean, select
from app.database import post, SessionDep, Vote as vote  # ✅ Import UserDep from database
from app.oauth2 import UserDep
from typing import Annotated, Optional
from app.database import UserOutput
from sqlalchemy import func
from sqlalchemy.orm import selectinload
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    title: str
    content: str
    owner_id: int
    owner: Optional[UserOutput] = None
    published: bool = False

class PostWithVotes(BaseModel):
    post: post
    votes: int
    owner: Optional[UserOutput] = None
    class Config:
        from_attributes = True

router = APIRouter(
    prefix = "/posts",
    tags = ["posts"],
)

# @router.get("/", response_model = list[Post]) #because the output is a list of posts
@router.get("/", response_model = list[PostWithVotes]) #because the output is a list of posts
def get_posts(session: SessionDep, current_user: UserDep, limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = session.exec(select(post).where(post.title.contains(search)).offset(skip).limit(limit)).all()
    # print(posts)
    results = session.exec(
    select(post, func.count(vote.post_id).label("votes"))
    .join(vote, post.id == vote.post_id, isouter=True)
    .options(selectinload(post.owner))  # Eager load the owner
    .group_by(post.id)
    .where(post.title.contains(search))
    .offset(skip)
    .limit(limit)
    ).all()
    posts_with_votes = []
    for post_obj, vote_count in results:
        # print("post_obj is", post_obj)
        # print("owner is ", post_obj.owner)
        post_with_votes = PostWithVotes(
            post=post_obj,      # Pass the entire post object
            votes=vote_count,
            owner=UserOutput(id = post_obj.owner.id, email = post_obj.owner.email, created_at= post_obj.owner.created_at)
        )
        posts_with_votes.append(post_with_votes)

    return posts_with_votes


# DEPENDS FUNCTIONS - Run for EVERY request
# Unlike lifespan which runs once, these dependencies execute for each POST request:
# - SessionDep: Creates a new database session for this specific request
# - UserDep: Authenticates the user for this specific request
# Performance impact: HIGH - runs for every single request

# PARALLELIZATION STATUS:
# ✅ HTTP LEVEL: AsyncIO handles multiple HTTP requests concurrently
# ✅ CONNECTION LEVEL: 5 database connections available via lifespan
# ⚠️  DATABASE LEVEL: session.commit() is BLOCKING (synchronous)
# 
# CURRENT BEHAVIOR:
# - Multiple users can send requests simultaneously (AsyncIO)
# - Each gets a different database connection (connection pooling)
# - BUT: database writes block each other (session.commit() is sync)
# 
# TO ACHIEVE TRUE PARALLELIZATION:
# - Need async database operations (await session.commit())
# - Or use background tasks for database writes
# - Current setup: parallel connections, serialized database operations
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = Post) #This refines the output type
async def create_posts(
    post_data: PostCreate, 
    session: SessionDep,      # ✅ DEPENDS: Fresh DB session for THIS request
    current_user: UserDep     # ✅ DEPENDS: User auth for THIS request
):
    # ... your code
    #post_data refine the input type
    # Create a SQLModel instance manually
    db_post = post(
        title=post_data.title,
        content=post_data.content,
        owner_id=current_user.id
    )
    # print(db_post)
    session.add(db_post)
    
    # ⚠️ BLOCKING OPERATION - Limits Parallelization:
    # This synchronous commit blocks the entire request until database write completes
    # Even with 5 connections, other requests must wait for this to finish
    # For true parallelization: use await session.commit() with async SQLAlchemy
    session.commit()
    session.refresh(db_post)
    return db_post

@router.get("/{id}", response_model=Post)
def get_post(id: int, session: SessionDep, current_user: UserDep):
    db_post = session.get(post, id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        ) 
    return db_post  # ✅ Returns Post object directly


@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep, current_user: UserDep):
    db_post = session.get(post, id)  # ✅ Use db_post instead of post
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        ) 
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this post")
    session.delete(db_post)
    session.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = Post) #because the output is a single post
def update_post(id: int, post_data: PostCreate, session: SessionDep, current_user: UserDep):
    # Get the existing post from database
    existing_post = session.get(post, id)
    
    # Check if post exists
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  
            detail=f"Post with id: {id} was not found"
        )
        # ✅ ADD THIS: Check if user owns the post
    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not allowed to update this post"
        )
    # Update the post attributes
    existing_post.title = post_data.title
    existing_post.content = post_data.content
    existing_post.owner_id = current_user.id
    
    # Commit the changes
    session.commit()
    session.refresh(existing_post)
    
    return existing_post

