import pytest
from app import database
from jose import jwt
from app.config import settings
from .conftest import client, test_engine, test_db, override_get_session

def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.json().get("message") == 'Hello World from Ann Arbor'
    assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json = {"email": "hello123@gmail.com", "password": "password123"})
    print(res.json())
    new_user = database.UserOutput(**res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201   

#to make it independent, we need to create a test user as fixture
def test_login_user(client, test_user):
    res = client.post(
        "/auth/login", data = {"username": test_user["email"], "password": test_user["password"]}
    )
    login_res = database.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms= settings.algorithm)
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "password123", 403),
    ("hello123@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
])
def test_invalid_login(client, test_user, email, password, status_code):
    # res = client.post(
    #     "/login", data = {"username": test_user["email"], "password": "wrong_password"}
    # )
    res = client.post(
        "/auth/login", data = {"username": email, "password": password}
    )
    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid Credentials"
