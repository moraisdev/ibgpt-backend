from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_representative_name = Column(String(100), index=True, nullable=False)
    company_representative_last_name = Column(String(100), index=True, nullable=False)
    company_representative_email = Column(
        String(255), unique=True, index=True, nullable=False
    )
    company_representative_phone_number = Column(
        String(20), unique=True, index=True, nullable=False
    )
    company_name = Column(String(255), index=True, nullable=False)
    company_email = Column(String(255), unique=True, index=True, nullable=False)
    company_phone_number = Column(String(20), unique=True, index=True, nullable=False)
    company_website = Column(String(255), nullable=False)
    company_activity_sector = Column(String(100), nullable=False)
    company_cnpj = Column(String(14), index=True, nullable=False, unique=True)
    company_address_street = Column(String(255), nullable=False)
    company_address_number = Column(String(255), nullable=False)
    company_address_complement = Column(String(255), nullable=True)
    company_address_neighbourhood = Column(String(255), nullable=False)
    company_address_city = Column(String(255), nullable=False)
    company_address_state = Column(String(255), nullable=False)
    company_address_country = Column(String(255), nullable=False)
    company_address_zip_code = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=True, default=True)
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

    user = relationship("User", back_populates="customers")

    offers = relationship("Offer", back_populates="customer")
