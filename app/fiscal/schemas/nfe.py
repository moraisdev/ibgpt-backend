from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class NfeItemResponse(_CamelModel):
    id: int
    chave: str | None = None
    numero: int | None = None
    serie: int | None = None
    modelo: int | None = None
    cnpj_emitente: str | None = None
    nome_emitente: str | None = None
    cnpj_destinatario: str | None = None
    nome_destinatario: str | None = None
    data_emissao: datetime | None = None
    valor_total: Decimal | None = None
    status: str | None = None
    tipo: str | None = None


class PaginatedNfeResponse(_CamelModel):
    items: list[NfeItemResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    valor_total_geral: Decimal | None = None
    total_processadas: int | None = None
    total_pendentes: int | None = None


class NfseItemResponse(_CamelModel):
    id: int
    numero: str | None = None
    tipo: str | None = None
    data_emissao: datetime | None = None
    prestador_cnpj: str | None = None
    prestador_razao_social: str | None = None
    tomador_cpf_cnpj: str | None = None
    tomador_razao_social: str | None = None
    municipio_codigo: str | None = None
    discriminacao: str | None = None
    valor_servicos: Decimal | None = None
    valor_iss: Decimal | None = None
    status: str | None = None


class PaginatedNfseResponse(_CamelModel):
    items: list[NfseItemResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


_MODAL_MAP = {1: "rodoviario", 2: "aereo", 3: "aquaviario", 4: "ferroviario", 5: "dutoviario"}
_TIPO_SERVICO_MAP = {0: "normal", 1: "subcontratacao", 2: "redespacho", 3: "redespacho_intermediario"}


def modal_label(code: int | None) -> str | None:
    """Convert modal integer code to human-readable label."""
    if code is None:
        return None
    return _MODAL_MAP.get(code, f"outro({code})")


def tipo_servico_label(code: int | None) -> str | None:
    """Convert tipo_servico integer code to human-readable label."""
    if code is None:
        return None
    return _TIPO_SERVICO_MAP.get(code, f"outro({code})")


class CteItemResponse(_CamelModel):
    """Item de listagem de CT-e."""

    id: int
    chave: str | None = None
    numero: int | None = None
    serie: int | None = None
    data_emissao: datetime | None = None
    cnpj_emitente: str | None = None
    nome_emitente: str | None = None
    cnpj_tomador: str | None = None
    nome_tomador: str | None = None
    modal: str | None = None
    tipo_servico: str | None = None
    valor_total: Decimal | None = None
    status: str | None = None


class PaginatedCteResponse(_CamelModel):
    """Resposta paginada de CT-e."""

    items: list[CteItemResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
