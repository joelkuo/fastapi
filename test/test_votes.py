import pytest
from app import database

@pytest.fixture
def test_votes(authorized_client, test_posts, test_db, test_user):
    vote = database.Vote(post_id = test_posts[0].id, user_id = test_user['id'])
    test_db.add(vote)
    test_db.commit()
    return vote

def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json = {"post_id": test_posts[-1].id,"dir": 1}) #don't test voting our own post
    assert res.status_code == 201

def test_vote_twice_post(authorized_client, test_posts, test_votes):
    res = authorized_client.post("/vote/", json = {"post_id": test_posts[0].id,"dir": 1})
    assert res.status_code == 409

def test_delete_vote(authorized_client, test_posts, test_votes):
    res = authorized_client.post("/vote/", json = {"post_id": test_posts[0].id,"dir": 0})
    assert res.status_code == 201

def test_delete_vote_non_exist(authorized_client,test_posts):
    res = authorized_client.post(
        "/vote/", json = {"post_id": test_posts[2].id, "dir" : 0}
    )
    assert res.status_code == 404

def test_vote_post_non_exist(authorized_client, test_posts):
    res = authorized_client.post(
        "/vote/", json = {"post_id": 80000, "dir": 1}
    )
    assert res.status_code == 404

def test_vote_unauthorized_user(client, test_posts):
    res = client.post(
        "/vote/", json = {"post_id": test_posts[2].id, "dir": 1}
    )
    assert res.status_code == 401