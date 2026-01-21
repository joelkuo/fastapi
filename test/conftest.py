from fastapi.testclient import TestClient
from httpx import _status_codes

from app.main import app

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config import settings

from app.database import get_session
from app.oauth2 import create_access_token
from app import database
# from app.database import Base


postgres_url = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"
@pytest.fixture()
def test_engine():
    """Create a fresh test database for each test"""
    # Create test engine
    engine = create_engine(postgres_url)
    # Create all tables, but NOT schema!
    SQLModel.metadata.create_all(engine)

    yield engine    
    # Create a session
    # with Session(engine) as session:
    #     yield session
    
    # Cleanup: drop all tables after test
    SQLModel.metadata.drop_all(engine)    

@pytest.fixture()
def test_db(test_engine):
    with Session(test_engine) as session:
        yield session
        session.rollback() 

@pytest.fixture()
def override_get_session(test_db):
    # test_db is injected by pytest here ✓
    
    def overrid_get_db():  # Regular function (not a fixture)
        yield test_db         # Captures test_db from outer scope
    
    app.dependency_overrides[get_session] = overrid_get_db
    yield
    # with TestClient(app) as test_client:
    #     yield test_client
    app.dependency_overrides.clear()

@pytest.fixture()
def client(override_get_session):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json = user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture()
def test_user2(client):
    user_data = {"email": "hello1234@gmail.com", "password": "password123"}
    res = client.post("/users/", json = user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture()
def token(test_user):
    return create_access_token( data = {"user_id": test_user["id"]})

@pytest.fixture()
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client

@pytest.fixture()
def test_posts(test_user, test_user2, test_db):
    posts_data = [
        {
            "title": "First Post",
            "content": "Content of the first test post",
            "owner_id": test_user["id"]
        },
        {
            "title": "Second Post",
            "content": "Another example post content",
            "owner_id": test_user["id"]
        },
        {
            "title": "Yet Another Post",
            "content": "Let's make sure we have multiple posts",
            "owner_id": test_user2["id"]
        },
    ]
    # Create Post objects from the posts_data and add to session
    # posts = [models.Post(**post) for post in posts_data]
    # session.add_all(posts)
    # session.commit()
    # session.refresh(posts[0])
    # session.refresh(posts[1])
    # session.refresh(posts[2])
    # return posts
    #Or we can use map function
    def create_post_model(post):
        return database.post(**post)


    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session = test_db
    session.add_all(posts)
    session.commit()
    return posts