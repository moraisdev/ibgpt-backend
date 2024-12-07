from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.offer import Offer
from sqlalchemy.orm import selectinload
from typing import List
from app.schemas.offer import OfferResponse
from app.models.calculations import InssSynthesizedCalculation
from sqlalchemy import delete, func, case, extract


async def save_offer(session: AsyncSession, offer: Offer) -> Offer:
    try:
        session.add(offer)
        await session.commit()
        await session.refresh(offer)
        return offer
    except Exception as e:
        await session.rollback()
        raise e


async def get_offer_by_id(session: AsyncSession, offer_id: int) -> Offer:
    result = await session.execute(select(Offer).where(Offer.id == offer_id))
    return result.scalar_one_or_none()


async def get_offer_with_relations(session: AsyncSession, offer_id: int) -> Offer:
    result = await session.execute(
        select(Offer)
        .options(
            selectinload(Offer.customer),
            selectinload(Offer.calculations),
        )
        .where(Offer.id == offer_id)
    )
    return result.scalar_one_or_none()


async def save_fine_tune_result(session: AsyncSession, offer: Offer, result_data: dict):
    for key, value in result_data.items():
        setattr(offer, key, value)

    async with session.begin():
        session.add(offer)
        await session.flush()
        await session.refresh(offer)

    return offer


async def get_offer_with_documents(session: AsyncSession, offer_id: int) -> Offer:
    result = await session.execute(
        select(Offer)
        .options(selectinload(Offer.documents), selectinload(Offer.calculations))
        .where(Offer.id == offer_id)
    )
    return result.scalars().one_or_none()


async def get_offers_by_user_id(
    session: AsyncSession, user_id: int
) -> List[OfferResponse]:
    result = await session.execute(
        select(Offer)
        .join(Offer.customer)
        .options(
            selectinload(Offer.customer),
            selectinload(Offer.calculations),
            selectinload(Offer.documents),
        )
        .where(Offer.customer.has(user_id=user_id))
    )
    offers = result.scalars().all()
    return offers


async def delete_calculations_by_offer_id(session: AsyncSession, offer_id: int):
    await session.execute(
        delete(InssSynthesizedCalculation).where(
            InssSynthesizedCalculation.offer_id == offer_id
        )
    )
    await session.commit()


async def save_calculation(
    session: AsyncSession,
    offer_id: int,
    description: str,
    values: dict,
) -> InssSynthesizedCalculation:
    calculation = InssSynthesizedCalculation(
        offer_id=offer_id,
        description=description,
        values=values,
    )
    session.add(calculation)
    await session.commit()
    await session.refresh(calculation)
    return calculation


async def get_dashboard_summary_repository(session: AsyncSession, user_id: int):
    query = await session.execute(
        select(
            func.count(Offer.id).label("total_offers"),
            func.sum(
                case((Offer.status == "sucesso", Offer.calculated_value), else_=0)
            ).label("total_success_offers_value"),
            func.sum(
                case(
                    (
                        (Offer.status == "pendente")
                        | (Offer.status == "processada")
                        | (Offer.status == "validada"),
                        Offer.calculated_value,
                    ),
                    else_=0,
                )
            ).label("total_pending_offers_value"),
            func.count(case((Offer.status == "pendente", 1))).label("pendente"),
            func.count(case((Offer.status == "processada", 1))).label("processada"),
            func.count(case((Offer.status == "sucesso", 1))).label("sucesso"),
            func.count(case((Offer.status == "encerrada", 1))).label("encerrada"),
            func.count(case((Offer.status == "validada", 1))).label("validada"),
        )
        .join(Offer.customer)
        .where(Offer.customer.has(user_id=user_id))
    )

    return query.first()._mapping


async def get_monthly_dashboard_data_repository(session: AsyncSession, user_id: int):
    query = await session.execute(
        select(
            extract("month", Offer.created_at).label("month"),
            func.count(case((Offer.status == "pendente", 1))).label("pendente"),
            func.count(case((Offer.status == "processada", 1))).label("processada"),
            func.count(case((Offer.status == "sucesso", 1))).label("sucesso"),
            func.count(case((Offer.status == "encerrada", 1))).label("encerrada"),
            func.count(case((Offer.status == "validada", 1))).label("validada"),
        )
        .join(Offer.customer)
        .where(Offer.customer.has(user_id=user_id))
        .group_by(extract("month", Offer.created_at))
        .order_by(extract("month", Offer.created_at))
    )

    monthly_data = {
        status: [0] * 12
        for status in ["pendente", "processada", "sucesso", "encerrada", "validada"]
    }

    for row in query.fetchall():
        row_mapping = row._mapping
        month_index = int(row_mapping["month"]) - 1
        for status in ["pendente", "processada", "sucesso", "encerrada", "validada"]:
            monthly_data[status][month_index] = row_mapping[status]

    return monthly_data


async def get_recovered_and_pending_repository(session: AsyncSession, user_id: int):
    query = await session.execute(
        select(
            extract("month", Offer.created_at).label("month"),
            func.sum(
                case((Offer.status == "sucesso", Offer.calculated_value), else_=0)
            ).label("success"),
            func.sum(
                case(
                    (
                        (Offer.status == "pendente")
                        | (Offer.status == "processada")
                        | (Offer.status == "validada"),
                        Offer.calculated_value,
                    ),
                    else_=0,
                )
            ).label("pending"),
        )
        .join(Offer.customer)
        .where(Offer.customer.has(user_id=user_id))
        .group_by(extract("month", Offer.created_at))
        .order_by(extract("month", Offer.created_at))
    )

    monthly_data = {"success": [0] * 12, "pending": [0] * 12}

    for row in query.fetchall():
        row_mapping = row._mapping
        month_index = int(row_mapping["month"]) - 1
        monthly_data["success"][month_index] = row_mapping["success"]
        monthly_data["pending"][month_index] = row_mapping["pending"]

    return monthly_data
