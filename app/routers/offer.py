from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.services.offer import (
    create_or_update_offer_service,
    update_offer_service,
    get_offer_resume_service,
    add_documents_to_offer_service,
    generate_ia_response_service,
)
from app.schemas.offer import OfferCreate, OfferResponse, OfferUpdate, FineTuneResponse
from typing import List

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
        processed_documents = await add_documents_to_offer_service(
            session, offer_id, files
        )
        return {
            "message": "Documentos processados com sucesso!",
            "documents": processed_documents,
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
