from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from app.database import SessionDep, Vote, VoteCreate, post
from app.oauth2 import UserDep

router = APIRouter(
    prefix = "/vote",
    tags = ["vote"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: VoteCreate, session: SessionDep, current_user: UserDep):
    post_obj = session.get(post, vote.post_id)
    if not post_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    vote_query = session.exec(select(Vote).where(Vote.user_id == current_user.id, Vote.post_id == vote.post_id))
    found_vote = vote_query.first()
    if found_vote:
        if vote.dir == 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already voted for this post")
        else:
            session.delete(found_vote)
            session.commit()
            return {"message": "successfully deleted vote"}
    else:
        if vote.dir == 1:
            new_vote = Vote(user_id=current_user.id, post_id=vote.post_id)
            session.add(new_vote)
            session.commit()
            return {"message": "successfully added vote"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote does not exist")