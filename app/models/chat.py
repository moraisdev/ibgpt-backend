from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary = Column(Text, nullable=True)

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

    user = relationship("User", back_populates="chats")

    messages = relationship(
        "ChatMessage", back_populates="chat", cascade="all, delete-orphan"
    )
