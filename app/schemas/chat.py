from pydantic import BaseModel
from typing import Optional, List
from app.schemas.chat_message import ChatMessageResponse


class ChatCreate(BaseModel):
    pass


class ChatSummaryResponse(BaseModel):
    chat_id: int
    preview: str

    class Config:
        orm_mode = True


class ChatResponse(BaseModel):
    id: int
    user_id: int
    summary: Optional[str] = None

    class Config:
        orm_mode = True


class ChatWithMessagesResponse(BaseModel):
    id: int
    user_id: int
    summary: Optional[str] = None
    messages: List[ChatMessageResponse] = []

    class Config:
        orm_mode = True
