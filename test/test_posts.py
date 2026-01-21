from app import database
from app.routers.post import Post

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200

def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_get_one_posts(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    # assert len(res.json()) == len(test_posts)
    post = Post(**res.json())
    assert post.id == test_posts[0].id
    assert res.status_code == 200

def test_get_one_postsnot_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/88888")
    assert res.status_code == 404

def test_unauthorized_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    # post = database.PostOut(**res.json())
    post = database.post(**res.json())
    assert res.status_code == 401

import pytest

@pytest.mark.parametrize(
    "title, content, published",
    [
        ("Post Example 1", "Content for example 1", True),
        ("Second Post", "Some more content", False),
        ("A third post", "Yet another example", True),
    ]
)
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("/posts/", json = {"title": title, "content": content, "published": published})
    created_post = Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.owner_id == test_user["id"]

def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post("/posts/", json = {"title": "random", "content": "random"})
    created_post = Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "random"
    assert created_post.content == "random"
    assert created_post.published == True
    assert created_post.owner_id == test_user["id"]

def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post("/posts/", json = {"title": "random", "content": "random"})    
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")    
    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204  # 204 No Content (successful delete)
    # Optionally, check that the post no longer exists
    # res_get = authorized_client.get(f"/posts/{test_posts[0].id}")
    # assert res_get.status_code == 404  # Post should not be found

def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/80000000")
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, test_user2, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[2].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }

    res = authorized_client.put(f"/posts/{test_posts[0].id}", json = data)
    updated_post = Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    res = authorized_client.put(f"/posts/{test_posts[2].id}", json = data)
    assert res.status_code == 403

def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}")    
    assert res.status_code == 401

def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    res = authorized_client.put(f"/posts/80000000", json = data)
    assert res.status_code == 404