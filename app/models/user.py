from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    func,
    text,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    last_name = Column(String(100), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    cnpj = Column(String(14), index=True, nullable=False, unique=True)
    company_name = Column(String(255), index=True, nullable=False)
    job_title = Column(String(255), index=True, nullable=False)

    role_id = Column(
        Integer, ForeignKey("roles.id"), nullable=False, server_default=text("3")
    )

    role = relationship("Role", back_populates="users")

    is_active = Column(Boolean, nullable=True, default=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    customers = relationship("Customer", back_populates="user")
