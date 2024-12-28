from pydantic import BaseModel
from typing import Optional


class ChatMessageCreate(BaseModel):
    content: str
    role: str


class ChatMessageResponse(BaseModel):
    id: int
    content: str
    role: str

    class Config:
        orm_mode = True
