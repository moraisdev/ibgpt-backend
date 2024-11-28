from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.customer import Customer


async def get_customer_by_cnpj(session: AsyncSession, cnpj: str) -> Customer | None:
    result = await session.execute(
        select(Customer).where(Customer.company_cnpj == cnpj)
    )
    return result.scalars().first()


async def get_all_customers(session: AsyncSession, user_id: int) -> list[Customer]:
    result = await session.execute(select(Customer).where(Customer.user_id == user_id))
    return result.scalars().all()


async def get_customer_by_id(
    session: AsyncSession, customer_id: int, user_id: int
) -> Customer | None:
    result = await session.execute(
        select(Customer).where(Customer.id == customer_id, Customer.user_id == user_id)
    )
    return result.scalars().first()


async def create_customer(session: AsyncSession, customer: Customer) -> Customer:
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def update_customer(session: AsyncSession, customer: Customer) -> Customer:
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def delete_customer(session: AsyncSession, customer: Customer):
    await session.delete(customer)
    await session.commit()
