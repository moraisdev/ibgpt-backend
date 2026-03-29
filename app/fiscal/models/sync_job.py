import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.fiscal.models.base import FiscalBase


class SyncJobStatus(enum.Enum):
    pendente = "pendente"
    sincronizando = "sincronizando"
    concluido = "concluido"
    falha = "falha"
    aguardando_retry = "aguardando_retry"


class SyncJob(FiscalBase):
    __tablename__ = "sync_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cnpj: Mapped[str] = mapped_column(
        String(14), ForeignKey("companies.cnpj"), index=True, nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[SyncJobStatus] = mapped_column(
        Enum(SyncJobStatus, name="sync_job_status"),
        default=SyncJobStatus.pendente,
        nullable=False,
    )
    progresso: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    etapa_atual: Mapped[str] = mapped_column(
        String(255), default="aguardando", nullable=False
    )
    pendencias: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    alertas: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    docs_downloaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SyncLog(FiscalBase):
    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    docs_downloaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_cstat: Mapped[str | None] = mapped_column(String(10), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("idx_sync_log_cnpj", "cnpj"),)
