from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status

from app.fiscal.deps import CurrentUser, DBSession, get_empresa_do_escritorio
from app.fiscal.models.company import Company, Contact
from app.fiscal.schemas.empresa import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    PaginatedEmpresaResponse,
)

router = APIRouter(prefix="/empresas", tags=["empresas"])


def _empresa_to_response(emp, sync_info: dict | None = None, doc_counts: dict | None = None) -> EmpresaResponse:
    anexos = emp.anexos_simples
    anexo_legado = emp.anexo_simples
    if not anexos and anexo_legado:
        anexos = [anexo_legado]
    if anexos and not anexo_legado:
        anexo_legado = anexos[0] if anexos else None

    ultima_sync = sync_info.get(emp.cnpj) if sync_info else None
    total_docs = doc_counts.get(emp.cnpj, 0) if doc_counts else 0

    return EmpresaResponse(
        cnpj=emp.cnpj,
        name=emp.name,
        uf_code=emp.uf_code,
        active=emp.active,
        cnae_principal=emp.cnae_principal,
        anexo_simples=anexo_legado,
        anexos_simples=anexos,
        iss_fixo=emp.iss_fixo,
        regime_caixa=emp.regime_caixa,
        tem_escrituracao_contabil=emp.tem_escrituracao_contabil,
        data_inicio_atividade=emp.data_inicio_atividade,
        parent_cnpj=emp.parent_cnpj,
        created_at=emp.created_at,
        tem_certificado=False,
        certificado_validade_fim=None,
        certificado_tipo=None,
        ultima_sync=ultima_sync,
        total_documentos=total_docs,
    )


@router.get(
    "",
    response_model=PaginatedEmpresaResponse,
    summary="Listar empresas",
    description="Retorna lista paginada de empresas.",
    status_code=status.HTTP_200_OK,
)
def listar_empresas(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Página (começa em 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    active: bool = Query(True, description="Filtrar por ativas/inativas"),
) -> PaginatedEmpresaResponse:
    query = db.query(Company).filter(Company.active == active)
    total = query.count()
    offset = (page - 1) * page_size
    empresas = query.offset(offset).limit(page_size).all()

    return PaginatedEmpresaResponse(
        items=[_empresa_to_response(e) for e in empresas],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.post(
    "",
    response_model=EmpresaResponse,
    summary="Cadastrar nova empresa",
    description="Cria empresa com os dados fornecidos. CNPJ deve ter 14 dígitos.",
    status_code=status.HTTP_201_CREATED,
)
def criar_empresa(
    payload: EmpresaCreate,
    db: DBSession,
    user: CurrentUser,
) -> EmpresaResponse:
    existente = db.query(Company).filter(Company.cnpj == payload.cnpj).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Empresa com CNPJ {payload.cnpj} já cadastrada",
        )

    anexo_simples = payload.anexo_simples
    anexos_simples = payload.anexos_simples
    if anexos_simples and not anexo_simples:
        anexo_simples = anexos_simples[0]
    elif anexo_simples and not anexos_simples:
        anexos_simples = [anexo_simples]

    empresa = Company(
        cnpj=payload.cnpj,
        name=payload.name,
        uf_code=payload.uf_code,
        cnae_principal=payload.cnae_principal,
        anexo_simples=anexo_simples,
        anexos_simples=anexos_simples,
        iss_fixo=payload.iss_fixo,
        regime_caixa=payload.regime_caixa,
        tem_escrituracao_contabil=payload.tem_escrituracao_contabil,
        data_inicio_atividade=payload.data_inicio_atividade,
        parent_cnpj=payload.parent_cnpj,
        created_at=datetime.now(timezone.utc),
    )
    db.add(empresa)

    contato = Contact(
        company_cnpj=payload.cnpj,
        nome=payload.name,
        email=payload.email,
        whatsapp=payload.whatsapp,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contato)

    db.commit()
    db.refresh(empresa)

    return _empresa_to_response(empresa)


@router.get(
    "/{cnpj}",
    response_model=EmpresaResponse,
    summary="Detalhes de uma empresa",
    description="Retorna dados completos de uma empresa pelo CNPJ.",
    status_code=status.HTTP_200_OK,
)
def detalhe_empresa(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
) -> EmpresaResponse:
    empresa = get_empresa_do_escritorio(cnpj, user, db)
    return _empresa_to_response(empresa)


@router.put(
    "/{cnpj}",
    response_model=EmpresaResponse,
    summary="Atualizar empresa",
    description="Atualiza campos da empresa. Apenas campos enviados são alterados.",
    status_code=status.HTTP_200_OK,
)
def atualizar_empresa(
    cnpj: str,
    payload: EmpresaUpdate,
    db: DBSession,
    user: CurrentUser,
) -> EmpresaResponse:
    empresa = get_empresa_do_escritorio(cnpj, user, db)
    update_data = payload.model_dump(exclude_none=True)

    if "anexos_simples" in update_data and "anexo_simples" not in update_data:
        update_data["anexo_simples"] = (
            update_data["anexos_simples"][0] if update_data["anexos_simples"] else None
        )
    elif "anexo_simples" in update_data and "anexos_simples" not in update_data:
        update_data["anexos_simples"] = (
            [update_data["anexo_simples"]] if update_data["anexo_simples"] else None
        )

    for campo, valor in update_data.items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return _empresa_to_response(empresa)


@router.delete(
    "/{cnpj}",
    summary="Desativar empresa",
    description="Desativa empresa (soft delete — mantém histórico).",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desativar_empresa(
    cnpj: str,
    db: DBSession,
    user: CurrentUser,
) -> None:
    empresa = get_empresa_do_escritorio(cnpj, user, db)
    empresa.active = False
    db.commit()
