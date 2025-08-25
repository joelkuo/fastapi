from fastapi import FastAPI, Response, status, HTTPException, Depends, Request
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
import time
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

CONNINFO = "postgresql://postgres:gzh960827@localhost:5432/fastapi"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the pool once on startup
    pool = ConnectionPool(CONNINFO, min_size=1, max_size=5, kwargs={"autocommit": True})
    app.state.pool = pool
    print("DB pool ready.")
    try:
        yield
    finally:
        pool.close()
        print("DB pool closed.")

# (Optional) dependency for nicer wiring
def get_pool(request: Request) -> ConnectionPool:
    return request.app.state.pool

app = FastAPI(lifespan = lifespan)


#in memory storage
my_posts = [{"title": "post 1", "content": "this is my first post", "id": 1}, {"title": "post2", "content": "this is my second post", "id": 2}]

def find_post(id):
    for p in my_posts:
        if str(p["id"]) == str(id):
            return p
    return

@app.get("/")
async def root():
    return {"message": "Hello World from Ann Arbor"}

@app.get("/posts")
def get_posts(pool: ConnectionPool = Depends(get_pool)):
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM posts;")
            return {"posts": cur.fetchall()}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
async def create_posts(post: Post, pool: ConnectionPool = Depends(get_pool)):
    # print(post)
    # print(post.title)
    # print(post.content)
    # print(post.published)
    # print(post.dict())
    # post_dict = post.dict()
    # post_dict["id"] = randrange(0, 10000000)
    # my_posts.append(post_dict)
    # return {"data": post_dict}
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
            new_post = cur.fetchone()
            conn.commit() #we need to commit the transaction, otherwise the data will not be saved
            return {"data": new_post}


    

# @app.get("/posts/latest")
# def get_latest_post():
#     post = my_posts[-1]
#     return {"post_detail": post}

@app.get("/posts/{id}")
def get_post(id: int, pool: ConnectionPool = Depends(get_pool)):
    # post = find_post(id)
    # print(post)
    # if not post:
    #     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
    #     # response.status_code = 404
    #     # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"post_detail": find_post(id)}
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM posts WHERE id = %s", (str(id),)) #need this extra comma, otherwise it will be a tuple and it will not work. 
            new_post = cur.fetchone()
            print(new_post)
            if not new_post:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
            return {"post_detail": new_post}

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if str(p['id']) == str(id):
            return i

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, pool: ConnectionPool = Depends(get_pool)):
    # index = find_index_post(id)
    # if not index:
    #     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
    # # print(index)
    # my_posts.pop(index)
    # return Response(status_code = status.HTTP_204_NO_CONTENT)
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
            deleted_post = cur.fetchone()
            conn.commit()#need to commit the transaction, otherwise the data will not be deleted
            print(deleted_post)
            if not deleted_post:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
            return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post, pool: ConnectionPool = Depends(get_pool)):
    # index = find_index_post(id)
    # if not index:
    #     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
    # post_dict = post.dict() #from FrontEnd
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    # return {"data": post_dict}
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
            updated_post = cur.fetchone()
            conn.commit()#need to commit the transaction, otherwise the data will not be deleted
            print(updated_post)
            if not updated_post:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
            return {"data": updated_post}