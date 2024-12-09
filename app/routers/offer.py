from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.services.offer import (
    create_or_update_offer_service,
    update_offer_service,
    get_offer_resume_service,
    add_documents_to_offer_service,
    generate_ia_response_service,
    generate_pdf_service,
    get_all_offers_service,
    update_calculations_service,
    get_dashboard_summary_service,
    get_monthly_dashboard_data_service,
    get_recovered_and_pending_service,
    delete_offer_service,
)
from app.schemas.offer import (
    OfferCreate,
    OfferResponse,
    OfferUpdate,
    FineTuneResponse,
    InssSynthesizedCalculationUpdate,
)
from typing import List
from fastapi.responses import FileResponse
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_offer(
    offer_data: OfferCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        created_offer = await create_or_update_offer_service(session, offer_data.dict())
        offer_with_relations = await get_offer_resume_service(session, created_offer.id)
        return offer_with_relations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a oferta: {str(e)}",
        )


@router.put("/{offer_id}", response_model=OfferResponse, status_code=status.HTTP_200_OK)
async def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        updated_offer = await update_offer_service(
            session, offer_id, offer_data.dict(exclude_unset=True)
        )
        return updated_offer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar a oferta: {str(e)}",
        )


@router.get(
    "/resume/{offer_id}", response_model=OfferResponse, status_code=status.HTTP_200_OK
)
async def get_offer_resume(
    offer_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        offer = await get_offer_resume_service(session, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oferta não encontrada.",
            )
        return offer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar a oferta: {str(e)}",
        )


@router.post("/documents/{offer_id}", status_code=status.HTTP_201_CREATED)
async def add_and_process_documents(
    offer_id: int,
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        await add_documents_to_offer_service( session, offer_id, files )
        return {
            "message": "Documentos processados com sucesso!"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao adicionar documentos: {e}"
        )


@router.get(
    "/generate-ia-response/{offer_id}",
    response_model=FineTuneResponse,
    status_code=status.HTTP_200_OK,
)
async def get_offer_and_use_fine_tune(
    offer_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result_data = await generate_ia_response_service(session, offer_id)
        return result_data
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@router.get(
    "/generate-pdf/{offer_id}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_pdf(
    offer_id: int, session: AsyncSession = Depends(get_async_session)
):
    try:
        file_path = await generate_pdf_service(offer_id, session)
        return FileResponse(
            file_path,
            filename=f"relatorio_{offer_id}.pdf",
            media_type="application/pdf",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar o PDF: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[OfferResponse],
    status_code=status.HTTP_200_OK,
    summary="Obter todas as ofertas do usuário autenticado",
)
async def get_all_offers(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        offers = await get_all_offers_service(session, current_user.id)
        return offers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar as ofertas: {str(e)}",
        )


@router.put("/update-calculations/{offer_id}", status_code=status.HTTP_200_OK)
async def update_calculations(
    offer_id: int,
    calculations: List[InssSynthesizedCalculationUpdate],
    session: AsyncSession = Depends(get_async_session),
):
    try:
        updated_calculations = await update_calculations_service(
            session, offer_id, calculations
        )
        return {
            "message": "Cálculos atualizados com sucesso!",
            "calculations": updated_calculations,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar os cálculos: {str(e)}",
        )


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_data(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        dashboard_data = await get_dashboard_summary_service(session, current_user.id)
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dados do dashboard: {str(e)}",
        )


@router.get("/dashboard/monthly", status_code=status.HTTP_200_OK)
async def get_monthly_dashboard_data(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        monthly_data = await get_monthly_dashboard_data_service(
            session, current_user.id
        )
        return monthly_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dados mensais do dashboard: {str(e)}",
        )


@router.get("/dashboard/recovered-and-pending", status_code=status.HTTP_200_OK)
async def get_recovered_and_pending(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        data = await get_recovered_and_pending_service(session, current_user.id)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar os valores do gráfico: {str(e)}",
        )


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(
    offer_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        await delete_offer_service(session, offer_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar a oferta: {str(e)}",
        )
