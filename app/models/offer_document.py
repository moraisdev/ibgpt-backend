from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    LargeBinary,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class OfferDocument(Base):
    __tablename__ = "offer_documents"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(LargeBinary, nullable=False)
    processed_text = Column(Text, nullable=True)

    offer = relationship("Offer", back_populates="documents")
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
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
