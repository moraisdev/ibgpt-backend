from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.offer import (
    save_offer,
    get_offer_by_id,
    get_offer_with_relations,
    get_offer_with_documents,
    get_offers_by_user_id,
    delete_calculations_by_offer_id,
    save_calculation,
    get_dashboard_summary_repository,
    get_monthly_dashboard_data_repository,
    get_recovered_and_pending_repository,
)
from typing import List
from fastapi import UploadFile
from app.models.offer import Offer
from app.models.offer_document import OfferDocument
from app.models.calculations import InssSynthesizedCalculation
from app.schemas.offer import (
    InssSynthesizedCalculationResponse,
    InssSynthesizedCalculationUpdate,
)
from fastapi import HTTPException, status
from app.services.extract_documents import extract_documents
from app.services.openai import prepare_prompt, use_fine_tuned_model
from sqlalchemy import delete
import json
from app.utils.generate_pdf_offer import render_offer_to_html
from weasyprint import HTML
from app.schemas.offer import OfferResponse


async def create_or_update_offer_service(session: AsyncSession, offer_data: dict):

    offer = Offer(**offer_data)

    saved_offer = await save_offer(session, offer)

    return saved_offer


async def update_offer_service(session: AsyncSession, offer_id: int, offer_data: dict):
    offer = await get_offer_with_relations(session, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta não encontrada.",
        )

    for key, value in offer_data.items():
        setattr(offer, key, value)

    return await save_offer(session, offer)


async def get_offer_resume_service(session: AsyncSession, offer_id: int):
    offer = await get_offer_with_relations(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada.")
    return offer


async def add_documents_to_offer_service(
    session: AsyncSession, offer_id: int, files: List[UploadFile]
):
    offer = await get_offer_by_id(session, offer_id)
    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Oferta não encontrada.",
        )

    processed_documents = []

    for file in files:
        content = await file.read()

        processed_text = extract_documents(content)

        document = OfferDocument(
            offer_id=offer_id,
            filename=file.filename,
            content=content,
            processed_text=processed_text,
        )

        session.add(document)
        processed_documents.append(
            {"filename": file.filename, "processed_text": processed_text}
        )

    await session.commit()

    return processed_documents


def process_fine_tune_response(fine_tune_response: dict) -> dict:
    try:
        offer_data = fine_tune_response.get("offer", {})

        calculations = []
        for resumo in offer_data.get("calculations", []):
            description = resumo.get("description", "Descrição Não Informada")
            values = resumo.get("values", {})

            calculations.append({"description": description, "values": values})

        return {
            "result_openai": json.dumps(offer_data),
            "accuracy_ia": offer_data.get("accuracy_ia", 0),
            "periodicity": offer_data.get("periodicity", ""),
            "calculated_value": offer_data.get("calculated_value", 0),
            "calculations": calculations,
        }
    except Exception as e:
        raise ValueError(f"Erro ao processar a resposta do modelo: {e}")


async def generate_ia_response_service(session: AsyncSession, offer_id: int) -> dict:
    offer = await get_offer_with_documents(session, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    prompt = await prepare_prompt(offer)

    fine_tune_response = await use_fine_tuned_model(prompt)

    result_data = process_fine_tune_response(fine_tune_response)

    offer.result_openai = result_data.get("result_openai")
    offer.accuracy_ia = result_data.get("accuracy_ia")
    offer.periodicity = result_data.get("periodicity")
    offer.calculated_value = result_data.get("calculated_value")
    offer.status = "processada"

    await session.execute(
        delete(InssSynthesizedCalculation).where(
            InssSynthesizedCalculation.offer_id == offer_id
        )
    )

    for calc_data in result_data.get("calculations", []):
        calculation = InssSynthesizedCalculation(
            description=calc_data["description"],
            values=calc_data["values"],
            offer_id=offer_id,
        )
        session.add(calculation)

    await session.commit()
    await session.refresh(offer)

    calculations_response = [
        InssSynthesizedCalculationResponse.model_validate(calc)
        for calc in offer.calculations
    ]

    response_data = {
        "result_openai": offer.result_openai,
        "accuracy_ia": offer.accuracy_ia,
        "periodicity": offer.periodicity,
        "calculated_value": offer.calculated_value,
        "calculations": calculations_response,
    }

    return response_data


async def generate_pdf_service(offer_id: int, session: AsyncSession) -> str:
    offer = await get_offer_with_relations(session, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta não encontrada.",
        )

    html_content = render_offer_to_html(offer)

    file_path = f"/tmp/relatorio_{offer_id}.pdf"

    HTML(string=html_content).write_pdf(file_path)

    return file_path


async def get_all_offers_service(
    session: AsyncSession, user_id: int
) -> List[OfferResponse]:
    offers = await get_offers_by_user_id(session, user_id)
    return offers


async def update_calculations_service(
    session: AsyncSession,
    offer_id: int,
    calculations: List[InssSynthesizedCalculationUpdate],
) -> List[InssSynthesizedCalculationResponse]:

    offer = await get_offer_with_relations(session, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta não encontrada.",
        )

    await delete_calculations_by_offer_id(session, offer_id)

    updated_calculations = []
    for calc in calculations:
        new_calculation = await save_calculation(
            session,
            offer_id=offer_id,
            description=calc.description,
            values=calc.values,
        )
        updated_calculations.append(
            InssSynthesizedCalculationResponse(
                id=new_calculation.id,
                description=new_calculation.description,
                values=new_calculation.values,
            )
        )

    return updated_calculations

async def get_dashboard_summary_service(session: AsyncSession, user_id: int):
    total_data = await get_dashboard_summary_repository(session, user_id)

    return {
        "total_offers": total_data["total_offers"],
        "offers_status": {
            "pendente": total_data["pendente"],
            "processada": total_data["processada"],
            "sucesso": total_data["sucesso"],
            "encerrada": total_data["encerrada"],
            "validada": total_data["validada"],
        },
        "total_success_offers_value": total_data["total_success_offers_value"],
        "total_pending_offers_value": total_data["total_pending_offers_value"],
    }


async def get_monthly_dashboard_data_service(session: AsyncSession, user_id: int):
    monthly_data = await get_monthly_dashboard_data_repository(session, user_id)

    labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    datasets = [
        {"label": "Processada", "color": "primary", "data": monthly_data["processada"]},
        {"label": "Sucesso", "color": "success", "data": monthly_data["sucesso"]},
        {"label": "Pendente", "color": "warning", "data": monthly_data["pendente"]},
        {"label": "Encerrada", "color": "secondary", "data": monthly_data["encerrada"]},
        {"label": "Validada", "color": "dark", "data": monthly_data["validada"]},
    ]

    return {"labels": labels, "datasets": datasets}


async def get_recovered_and_pending_service(session: AsyncSession, user_id: int):
    monthly_data = await get_recovered_and_pending_repository(session, user_id)

    labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    datasets = [
        {"label": "Recuperado", "color": "success", "data": monthly_data["success"]},
        {"label": "Pendente", "color": "warning", "data": monthly_data["pending"]},
    ]

    return {"labels": labels, "datasets": datasets}

async def delete_offer_service(session: AsyncSession, offer_id: int):
    offer = await get_offer_by_id(session, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta não encontrada.",
        )

    await session.delete(offer)
    await session.commit()