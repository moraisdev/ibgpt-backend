from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.offer import Offer
from sqlalchemy.orm import selectinload
from typing import List
from app.schemas.offer import OfferResponse

async def save_offer(session: AsyncSession, offer: Offer) -> Offer:
    if not session.in_transaction():
        async with session.begin():
            session.add(offer)
            await session.flush()
            await session.refresh(offer)
    else:
        session.add(offer)
        await session.flush()
        await session.refresh(offer)

    return offer


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


async def get_offers_by_user_id(session: AsyncSession, user_id: int) -> List[OfferResponse]:
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