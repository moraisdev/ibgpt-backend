"""Schemas dos endpoints de sincronizacao NF-e."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    """Modelo base com serializacao camelCase para o frontend."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SyncIniciarResponse(_CamelModel):
    """Resposta ao iniciar sincronizacao manual."""

    job_id: str
    cnpj: str
    status: str
    message: str


class SyncJobAtivoResponse(_CamelModel):
    """Status do job de sync ativo ou mais recente de uma empresa."""

    job_id: str
    status: str
    progresso: int = 0
    etapa_atual: str = ""
    docs_downloaded: int = 0
    erro: str | None = None
    created_at: datetime
    updated_at: datetime


class SyncStatusResponse(_CamelModel):
    """Status resumido do ultimo sync job de uma empresa."""

    cnpj: str
    job_id: str | None = None
    status: str | None = None
    progresso: int = 0
    etapa_atual: str = ""
    docs_downloaded: int = 0
    erro: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
