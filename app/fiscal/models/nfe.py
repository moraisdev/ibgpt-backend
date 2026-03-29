from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.fiscal.models.base import FiscalBase


class RawXmlDocument(FiscalBase):
    __tablename__ = "raw_xml_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_cnpj: Mapped[str] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), nullable=False
    )
    nsu: Mapped[str] = mapped_column(String(15), nullable=False)
    chave_acesso: Mapped[str | None] = mapped_column(String(44), nullable=True)
    schema_type: Mapped[str] = mapped_column(String(100), nullable=False)
    xml_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ambiente: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    nfe_document: Mapped["NfeDocument"] = relationship(
        back_populates="raw_xml", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("company_cnpj", "nsu", "ambiente", name="uq_raw_xml_cnpj_nsu_amb"),
        Index("idx_raw_xml_chave", "chave_acesso"),
        Index("idx_raw_xml_processed", "processed"),
    )


class NfeDocument(FiscalBase):
    __tablename__ = "nfe_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chave_acesso: Mapped[str] = mapped_column(String(44), unique=True, nullable=False)
    company_cnpj: Mapped[str] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), nullable=False
    )
    raw_xml_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("raw_xml_documents.id"), nullable=True
    )

    numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serie: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modelo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipo_operacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_emissao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data_saida: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    natureza_operacao: Mapped[str | None] = mapped_column(String(60), nullable=True)
    finalidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipo_impressao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forma_pagamento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codigo_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True)

    valor_produtos: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_frete: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_seguro: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_outras: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    status_sefaz: Mapped[str | None] = mapped_column(String(10), nullable=True)
    protocolo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_autorizacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    manifest_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    raw_xml: Mapped["RawXmlDocument"] = relationship(back_populates="nfe_document")
    emitente: Mapped["NfeEmitente"] = relationship(
        back_populates="nfe", uselist=False, cascade="all, delete-orphan"
    )
    destinatario: Mapped["NfeDestinatario"] = relationship(
        back_populates="nfe", uselist=False, cascade="all, delete-orphan"
    )
    items: Mapped[list["NfeItem"]] = relationship(
        back_populates="nfe", cascade="all, delete-orphan"
    )
    impostos: Mapped["NfeImposto"] = relationship(
        back_populates="nfe", uselist=False, cascade="all, delete-orphan"
    )
    eventos: Mapped[list["NfeEvento"]] = relationship(
        back_populates="nfe", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_nfe_chave", "chave_acesso"),
        Index("idx_nfe_company_data", "company_cnpj", "data_emissao"),
        Index("idx_nfe_status", "status_sefaz"),
        Index("idx_nfe_data_emissao", "data_emissao"),
    )


class NfeEmitente(FiscalBase):
    __tablename__ = "nfe_emitentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nfe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nfe_documents.id"), nullable=False
    )

    cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(11), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(20), nullable=True)
    razao_social: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255), nullable=True)

    logradouro: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(60), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(60), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(60), nullable=True)
    codigo_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True)
    municipio: Mapped[str | None] = mapped_column(String(60), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(8), nullable=True)
    pais: Mapped[str | None] = mapped_column(String(60), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    nfe: Mapped["NfeDocument"] = relationship(back_populates="emitente")

    __table_args__ = (Index("idx_emit_cnpj", "cnpj"),)


class NfeDestinatario(FiscalBase):
    __tablename__ = "nfe_destinatarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nfe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nfe_documents.id"), nullable=False
    )

    cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(11), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(20), nullable=True)
    razao_social: Mapped[str | None] = mapped_column(String(255), nullable=True)

    logradouro: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(60), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(60), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(60), nullable=True)
    codigo_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True)
    municipio: Mapped[str | None] = mapped_column(String(60), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(8), nullable=True)
    pais: Mapped[str | None] = mapped_column(String(60), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    nfe: Mapped["NfeDocument"] = relationship(back_populates="destinatario")

    __table_args__ = (Index("idx_dest_cnpj", "cnpj"),)


class NfeItem(FiscalBase):
    __tablename__ = "nfe_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nfe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nfe_documents.id"), nullable=False
    )
    numero_item: Mapped[int] = mapped_column(Integer, nullable=False)

    codigo: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ean: Mapped[str | None] = mapped_column(String(14), nullable=True)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ncm: Mapped[str | None] = mapped_column(String(8), nullable=True)
    cest: Mapped[str | None] = mapped_column(String(7), nullable=True)
    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(6), nullable=True)
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    valor_unitario: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    origem: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cst_icms: Mapped[str | None] = mapped_column(String(3), nullable=True)
    base_icms: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    aliq_icms: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    valor_icms: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    cst_pis: Mapped[str | None] = mapped_column(String(2), nullable=True)
    base_pis: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    aliq_pis: Mapped[Decimal | None] = mapped_column(Numeric(7, 4), nullable=True)
    valor_pis: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    cst_cofins: Mapped[str | None] = mapped_column(String(2), nullable=True)
    base_cofins: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    aliq_cofins: Mapped[Decimal | None] = mapped_column(Numeric(7, 4), nullable=True)
    valor_cofins: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    cst_ipi: Mapped[str | None] = mapped_column(String(2), nullable=True)
    valor_ipi: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    nfe: Mapped["NfeDocument"] = relationship(back_populates="items")

    __table_args__ = (Index("idx_items_nfe", "nfe_id"),)


class NfeImposto(FiscalBase):
    __tablename__ = "nfe_impostos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nfe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nfe_documents.id"), nullable=False, unique=True
    )

    base_icms: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_icms: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_icms_deson: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    base_icms_st: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_icms_st: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_fcp: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_fcp_st: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_fcp_st_ret: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    valor_produtos: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_frete: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_seguro: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_desconto: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_ii: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_ipi: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_ipi_devol: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_pis: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_cofins: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_outras: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_nf: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_tributos: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    nfe: Mapped["NfeDocument"] = relationship(back_populates="impostos")


class NfeEvento(FiscalBase):
    __tablename__ = "nfe_eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nfe_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nfe_documents.id"), nullable=True
    )
    chave_acesso: Mapped[str] = mapped_column(String(44), nullable=False)

    tipo_evento: Mapped[str] = mapped_column(String(10), nullable=False)
    sequencia: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    data_evento: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    protocolo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    descricao_evento: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_sefaz: Mapped[str | None] = mapped_column(String(10), nullable=True)
    xml_evento: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    nfe: Mapped["NfeDocument"] = relationship(back_populates="eventos")

    __table_args__ = (
        Index("idx_eventos_chave", "chave_acesso"),
        Index("idx_eventos_tipo", "tipo_evento"),
        Index("idx_eventos_nfe", "nfe_id"),
    )
