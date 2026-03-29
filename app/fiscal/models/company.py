"""Modelos de empresa para o módulo fiscal."""

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.fiscal.models.base import FiscalBase


class Company(FiscalBase):
    """Company registered for NFe sync."""

    __tablename__ = "companies"

    cnpj: Mapped[str] = mapped_column(String(14), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    uf_code: Mapped[int] = mapped_column(Integer, nullable=False)
    escritorio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cert_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cert_pass: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cert_pass_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_cnpj: Mapped[str | None] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), nullable=True
    )
    iss_fixo: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    regime_caixa: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    regime_caixa_ano_vigencia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tem_escrituracao_contabil: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    regime_historico: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cnae_principal: Mapped[str | None] = mapped_column(String(7), nullable=True)
    anexo_simples: Mapped[str | None] = mapped_column(String(5), nullable=True)
    anexos_simples: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_mei: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    data_inicio_atividade: Mapped[date | None] = mapped_column(Date, nullable=True)
    folha_pagamento_12m: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    rbt12_manual: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    procuracao_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    procuracao_verificada_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    procuracao_codigo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    optou_cbs_fora_das: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    opcao_cbs_semestre: Mapped[str | None] = mapped_column(String(7), nullable=True)
    opcao_cbs_historico: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    nsu_control: Mapped["NsuControl"] = relationship(back_populates="company", uselist=False)
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    parent: Mapped["Company | None"] = relationship(
        "Company", remote_side=[cnpj], foreign_keys=[parent_cnpj]
    )
    children: Mapped[list["Company"]] = relationship(
        "Company", back_populates="parent", foreign_keys=[parent_cnpj]
    )

    __table_args__ = (
        Index("idx_companies_active", "active"),
        Index("idx_companies_parent", "parent_cnpj"),
        Index("idx_companies_cnae", "cnae_principal"),
        Index("idx_companies_escritorio", "escritorio_id"),
    )


class NsuControl(FiscalBase):
    """NSU control for sync tracking per company and environment."""

    __tablename__ = "nsu_control"

    cnpj: Mapped[str] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), primary_key=True
    )
    ambiente: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    last_nsu: Mapped[str] = mapped_column(
        String(15), default="000000000000000", nullable=False
    )
    max_nsu: Mapped[str] = mapped_column(
        String(15),
        default="000000000000000",
        nullable=False,
        server_default="000000000000000",
    )
    cooldown_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_docs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="nsu_control")


class Contact(FiscalBase):
    """Contato vinculado a uma empresa (email/WhatsApp)."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_cnpj: Mapped[str] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    company: Mapped["Company"] = relationship(back_populates="contacts")

    __table_args__ = (
        Index("idx_contacts_company", "company_cnpj"),
        Index("idx_contacts_active", "company_cnpj", "active"),
    )
