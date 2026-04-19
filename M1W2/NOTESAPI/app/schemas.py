from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type:str = "bearer"

class NoteCreate(BaseModel):
    title: str = Field(..., max_length=100, min_length=2)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default=[])

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None

class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]        # ← reads from @property, not tags_str!
    owner_id: int | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class NoteListResponse(BaseModel):
    count: int
    notes: list[NoteResponse]
