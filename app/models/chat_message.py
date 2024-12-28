from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.models.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)

    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    chat = relationship("Chat", back_populates="messages")

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('America/Sao_Paulo', now())"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('America/Sao_Paulo', now())"),
        onupdate=text("timezone('America/Sao_Paulo', now())"),
        nullable=False,
    )
