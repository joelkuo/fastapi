from pydantic import BaseModel

class TokenData(BaseModel):
    id: int | None = None
    email: str | None = None