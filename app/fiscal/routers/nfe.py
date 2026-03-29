from datetime import datetime

from fastapi import APIRouter, Query, status
from sqlalchemy import func

from app.fiscal.deps import CurrentUser, DBSession, get_empresa_do_escritorio
from app.fiscal.models.nfe import NfeDocument, NfeEmitente, NfeDestinatario
from app.fiscal.schemas.nfe import NfeItemResponse, PaginatedNfeResponse

router = APIRouter(prefix="/nfe", tags=["nfe"])

_CSIT_MAP = {"1": "Autorizada", "2": "Denegada", "3": "Cancelada"}


def _nfe_to_response(nfe, tipo: str) -> NfeItemResponse:
    raw_status = nfe.status_sefaz or ""
    display_status = _CSIT_MAP.get(raw_status, raw_status) if raw_status else ""

    return NfeItemResponse(
        id=nfe.id,
        chave=nfe.chave_acesso,
        numero=nfe.numero,
        serie=nfe.serie,
        modelo=nfe.modelo,
        cnpj_emitente=nfe.emitente.cnpj if nfe.emitente else "",
        nome_emitente=nfe.emitente.razao_social if nfe.emitente else "",
        cnpj_destinatario=nfe.destinatario.cnpj if nfe.destinatario else "",
        nome_destinatario=nfe.destinatario.razao_social if nfe.destinatario else "",
        data_emissao=nfe.data_emissao,
        valor_total=nfe.valor_total,
        status=display_status,
        tipo=tipo,
    )


def _parse_competencia(mes: int | None, ano: int | None) -> tuple[datetime | None, datetime | None]:
    if mes is None or ano is None:
        return None, None
    data_inicio = datetime(ano, mes, 1)
    if mes == 12:
        data_fim = datetime(ano + 1, 1, 1)
    else:
        data_fim = datetime(ano, mes + 1, 1)
    return data_inicio, data_fim


def _build_response(
    db,
    cnpj: str,
    tipo: str,
    page: int,
    page_size: int,
    mes: int | None = None,
    ano: int | None = None,
) -> PaginatedNfeResponse:
    data_inicio, data_fim = _parse_competencia(mes, ano)
    tipo_operacao = 1 if tipo == "saida" else 0

    query = db.query(NfeDocument).filter(
        NfeDocument.company_cnpj == cnpj,
        NfeDocument.tipo_operacao == tipo_operacao,
    )

    if data_inicio is not None:
        query = query.filter(NfeDocument.data_emissao >= data_inicio)
    if data_fim is not None:
        query = query.filter(NfeDocument.data_emissao < data_fim)

    total = query.count()
    offset = (page - 1) * page_size
    nfes = query.offset(offset).limit(page_size).all()

    valor_total_geral = (
        db.query(func.sum(NfeDocument.valor_total))
        .filter(
            NfeDocument.company_cnpj == cnpj,
            NfeDocument.tipo_operacao == tipo_operacao,
            *([NfeDocument.data_emissao >= data_inicio] if data_inicio else []),
            *([NfeDocument.data_emissao < data_fim] if data_fim else []),
        )
        .scalar()
    )

    items = [_nfe_to_response(n, tipo) for n in nfes]
    processadas = sum(1 for i in items if i.status in ("Autorizada", "Processada"))
    pendentes = total - processadas

    return PaginatedNfeResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
        valor_total_geral=valor_total_geral,
        total_processadas=processadas,
        total_pendentes=pendentes,
    )


@router.get(
    "/{cnpj}/saida",
    response_model=PaginatedNfeResponse,
    summary="Listar NF-e de saída",
    status_code=status.HTTP_200_OK,
)
def listar_nfe_saida(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mes: int | None = Query(None, ge=1, le=12),
    ano: int | None = Query(None, ge=2020, le=2030),
) -> PaginatedNfeResponse:
    get_empresa_do_escritorio(cnpj, user, db)
    return _build_response(db, cnpj, "saida", page, page_size, mes, ano)


@router.get(
    "/{cnpj}/entrada",
    response_model=PaginatedNfeResponse,
    summary="Listar NF-e de entrada",
    status_code=status.HTTP_200_OK,
)
def listar_nfe_entrada(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mes: int | None = Query(None, ge=1, le=12),
    ano: int | None = Query(None, ge=2020, le=2030),
) -> PaginatedNfeResponse:
    get_empresa_do_escritorio(cnpj, user, db)
    return _build_response(db, cnpj, "entrada", page, page_size, mes, ano)
