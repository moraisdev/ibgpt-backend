from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class EmpresaCreate(_CamelModel):
    cnpj: str
    name: str
    uf_code: int
    cnae_principal: str | None = None
    anexo_simples: str | None = None
    anexos_simples: list[str] | None = None
    iss_fixo: bool = False
    regime_caixa: bool = False
    tem_escrituracao_contabil: bool = False
    data_inicio_atividade: date | None = None
    parent_cnpj: str | None = None
    email: str
    whatsapp: str | None = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_somente_digitos(cls, v: str) -> str:
        digits = v.replace(".", "").replace("/", "").replace("-", "")
        if not digits.isdigit() or len(digits) != 14:
            raise ValueError("CNPJ inválido — informe 14 dígitos")
        return digits

    @field_validator("anexo_simples")
    @classmethod
    def anexo_valido(cls, v: str | None) -> str | None:
        if v is not None and v not in ("I", "II", "III", "IV", "V"):
            raise ValueError("Anexo deve ser I, II, III, IV ou V")
        return v

    @field_validator("anexos_simples")
    @classmethod
    def anexos_validos(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            validos = {"I", "II", "III", "IV", "V"}
            for anexo in v:
                if anexo not in validos:
                    raise ValueError(f"Anexo '{anexo}' invalido. Deve ser I, II, III, IV ou V")
        return v

    @field_validator("uf_code")
    @classmethod
    def uf_code_valido(cls, v: int) -> int:
        if not (10 <= v <= 53):
            raise ValueError("UF inválida")
        return v


class EmpresaUpdate(_CamelModel):
    name: str | None = None
    uf_code: int | None = None
    cnae_principal: str | None = None
    anexo_simples: str | None = None
    anexos_simples: list[str] | None = None
    iss_fixo: bool | None = None
    regime_caixa: bool | None = None
    tem_escrituracao_contabil: bool | None = None
    data_inicio_atividade: date | None = None
    parent_cnpj: str | None = None
    active: bool | None = None


class EmpresaResponse(_CamelModel):
    cnpj: str
    name: str
    uf_code: int
    active: bool
    cnae_principal: str | None = None
    anexo_simples: str | None = None
    anexos_simples: list[str] | None = None
    iss_fixo: bool
    regime_caixa: bool
    tem_escrituracao_contabil: bool
    data_inicio_atividade: date | None = None
    parent_cnpj: str | None = None
    created_at: datetime
    tem_certificado: bool = False
    certificado_validade_fim: datetime | None = None
    certificado_tipo: str | None = None
    ultima_sync: datetime | None = None
    total_documentos: int = 0


class PaginatedEmpresaResponse(_CamelModel):
    items: list[EmpresaResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
