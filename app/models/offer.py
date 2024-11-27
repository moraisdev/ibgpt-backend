from sqlalchemy import Column, Integer, String, Text, Float, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(255), nullable=False)
    offer_type = Column(String(50), nullable=False)
    documents = Column(String(255), nullable=False)
    data_processing_json = Column(String(255), nullable=False)
    accuracy_ia = Column(Float, nullable=False)
    periodicity = Column(String(50), nullable=False)
    calculated_value = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    liquidation_value = Column(Float, nullable=False)
    observations = Column(Text, nullable=True)
    results_json = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="offers")
