from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, ForeignKey, text
from sqlalchemy.orm import relationship
from app.models.base import Base


class InssSynthesizedCalculation(Base):
    __tablename__ = "inss_synthesized_calculations"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(
        Integer, ForeignKey("offers.id"), nullable=False
    )  # Relacionamento com a tabela 'offers'
    description = Column(
        String(255), nullable=False
    )  # Nome do cálculo (ex: "3 HORAS FÉRIAS")
    values = Column(
        JSON, nullable=False
    )  # Dados detalhados do cálculo (ex: {"BaseCalculoINSS": 839952.73, "CreditosAuditados": 167990.55, ...})

    # Relacionamento com a tabela Offer
    offer = relationship("Offer", back_populates="calculations")
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
