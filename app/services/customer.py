from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def create_customer_service(
    session: AsyncSession, customer_data: CustomerCreate, user_id: int
) -> Customer:
    new_customer = Customer(user_id=user_id, **customer_data.dict())
    session.add(new_customer)
    await session.commit()
    await session.refresh(new_customer)
    return new_customer


async def get_all_customers_service(
    session: AsyncSession, user_id: int
) -> list[Customer]:
    result = await session.execute(select(Customer).where(Customer.user_id == user_id))
    return result.scalars().all()


async def get_customer_by_id_service(
    session: AsyncSession, customer_id: int, user_id: int
) -> Customer | None:
    result = await session.execute(
        select(Customer).where(Customer.id == customer_id, Customer.user_id == user_id)
    )
    return result.scalars().first()


async def update_customer_service(
    session: AsyncSession, customer_id: int, customer_data: CustomerUpdate, user_id: int
) -> Customer:
    customer = await get_customer_by_id_service(session, customer_id, user_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado ou não pertence ao usuário.",
        )

    for key, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)

    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def delete_customer_service(
    session: AsyncSession, customer_id: int, user_id: int
):
    customer = await get_customer_by_id_service(session, customer_id, user_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado ou não pertence ao usuário.",
        )
    await session.delete(customer)
    await session.commit()
