import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status

from app.fiscal.deps import CurrentUser, DBSession, get_empresa_do_escritorio
from app.fiscal.models.sync_job import SyncJob, SyncJobStatus
from app.fiscal.schemas.sync import SyncIniciarResponse, SyncJobAtivoResponse, SyncStatusResponse

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get(
    "/{cnpj}/status",
    response_model=SyncStatusResponse,
    summary="Status do ultimo sync job",
    description="Retorna o status do último job de sincronização para uma empresa.",
    status_code=status.HTTP_200_OK,
)
def sync_status(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
) -> SyncStatusResponse:
    get_empresa_do_escritorio(cnpj, user, db)

    job = (
        db.query(SyncJob)
        .filter(SyncJob.cnpj == cnpj)
        .order_by(SyncJob.created_at.desc())
        .first()
    )

    if not job:
        return SyncStatusResponse(cnpj=cnpj)

    return SyncStatusResponse(
        cnpj=cnpj,
        job_id=job.id,
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        progresso=job.progresso,
        etapa_atual=job.etapa_atual,
        docs_downloaded=job.docs_downloaded,
        erro=job.erro,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post(
    "/{cnpj}/iniciar",
    response_model=SyncIniciarResponse,
    summary="Iniciar sincronizacao manual",
    description="Cria um SyncJob pendente para a empresa e retorna o ID do job.",
    status_code=status.HTTP_201_CREATED,
)
def iniciar_sync_manual(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
) -> SyncIniciarResponse:
    get_empresa_do_escritorio(cnpj, user, db)

    job_ativo = (
        db.query(SyncJob)
        .filter(
            SyncJob.cnpj == cnpj,
            SyncJob.status.in_([SyncJobStatus.pendente, SyncJobStatus.sincronizando]),
        )
        .first()
    )
    if job_ativo:
        return SyncIniciarResponse(
            job_id=job_ativo.id,
            cnpj=cnpj,
            status=job_ativo.status.value if hasattr(job_ativo.status, "value") else str(job_ativo.status),
            message="Sincronizacao ja esta em andamento",
        )

    job = SyncJob(
        id=str(uuid.uuid4()),
        cnpj=cnpj,
        user_id=user.id,
        status=SyncJobStatus.pendente,
        etapa_atual="aguardando",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return SyncIniciarResponse(
        job_id=job.id,
        cnpj=cnpj,
        status="pendente",
        message="Sincronizacao agendada com sucesso",
    )


@router.get(
    "/{cnpj}/job-ativo",
    response_model=SyncJobAtivoResponse | None,
    summary="Job de sync ativo ou recente",
    description="Retorna o job de sync mais recente (ativo ou concluido nas ultimas 24h).",
    status_code=status.HTTP_200_OK,
)
def sync_job_ativo(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
) -> SyncJobAtivoResponse | None:
    get_empresa_do_escritorio(cnpj, user, db)

    job = (
        db.query(SyncJob)
        .filter(
            SyncJob.cnpj == cnpj,
            SyncJob.status.in_([SyncJobStatus.pendente, SyncJobStatus.sincronizando]),
        )
        .order_by(SyncJob.created_at.desc())
        .first()
    )

    if not job:
        cutoff_concluido = datetime.now(timezone.utc) - timedelta(minutes=30)
        job = (
            db.query(SyncJob)
            .filter(
                SyncJob.cnpj == cnpj,
                SyncJob.status == SyncJobStatus.concluido,
                SyncJob.created_at >= cutoff_concluido,
            )
            .order_by(SyncJob.created_at.desc())
            .first()
        )

    if not job:
        cutoff_falha = datetime.now(timezone.utc) - timedelta(minutes=5)
        job = (
            db.query(SyncJob)
            .filter(
                SyncJob.cnpj == cnpj,
                SyncJob.status == SyncJobStatus.falha,
                SyncJob.created_at >= cutoff_falha,
            )
            .order_by(SyncJob.created_at.desc())
            .first()
        )

    if not job:
        return None

    return SyncJobAtivoResponse(
        job_id=job.id,
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        progresso=job.progresso,
        etapa_atual=job.etapa_atual,
        docs_downloaded=job.docs_downloaded,
        erro=job.erro,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
