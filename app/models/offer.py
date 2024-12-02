from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    TIMESTAMP,
    ForeignKey,
    text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=True
    )  # id da empresa
    status = Column(String(255), nullable=True)  # status da proposta
    offer_type = Column(
        String(50), nullable=True
    )  # tipo da proposta ex ( verbas indenizatorias INSS)

    # Dados da proposta
    company_service_type = Column(
        String(50), nullable=True
    )  # tipo de serviço da empresa ex ( servico ou produto )
    company_profit_type = Column(
        String(50), nullable=True
    )  # tipo de lucro da empresa ex ( presumido )
    company_time_profit_type = Column(
        String(50), nullable=True
    )  # tipo de lucro da empresa ex ( presumido )
    company_work_regime = Column(
        String(50), nullable=True
    )  # regime de trabalho da empresa ex ( CLT ou PJ )
    company_clt_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa
    company_pj_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa
    company_freelance_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa
    company_internship_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa
    company_cooperative_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa
    company_total_employees = Column(
        Integer, nullable=True
    )  # numero de funcionarios da empresa

    # Oferta
    accuracy_ia = Column(Float, nullable=True)  # gerado por IA precisão da oferta
    periodicity = Column(
        String(50), nullable=True
    )  # gerado por IA periodo estipulado na oferta
    calculated_value = Column(
        Float, nullable=True
    )  # gerado por IA  valor calculado da oferta
    commission = Column(Float, nullable=True)  # gerado por IA  comissão da oferta
    liquidation_value = Column(
        Float, nullable=True
    )  # NAO GERADO POR IA valor liquidado da oferta
    observations = Column(
        Text, nullable=True
    )  # NAO GERADO POR IA observações da oferta
    result_openai = Column(
        Text, nullable=True
    )  # SALVA O JSON INTEIRO RETORNADO da resposta da IA

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

    calculations = relationship(
        "InssSynthesizedCalculation",
        back_populates="offer",
        cascade="all, delete-orphan",
    )  # calculos sintezados da oferta
    documents = relationship(
        "OfferDocument", back_populates="offer", cascade="all, delete-orphan"
    )  # documentos associados à oferta
    customer = relationship(
        "Customer", back_populates="offers"
    )  # empresa associada a oferta
