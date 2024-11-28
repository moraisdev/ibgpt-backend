from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.repositories.customer import (
    get_customer_by_cnpj,
    get_all_customers,
    get_customer_by_id,
    create_customer,
    update_customer,
    delete_customer,
)


async def create_customer_service(
    session: AsyncSession, customer_data: CustomerCreate, user_id: int
) -> Customer:
    existing_customer = await get_customer_by_cnpj(session, customer_data.company_cnpj)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cliente cadastrado com este CNPJ.",
        )

    new_customer = Customer(user_id=user_id, **customer_data.dict())
    return await create_customer(session, new_customer)


async def get_all_customers_service(
    session: AsyncSession, user_id: int
) -> list[Customer]:
    return await get_all_customers(session, user_id)


async def get_customer_by_id_service(
    session: AsyncSession, customer_id: int, user_id: int
) -> Customer:
    customer = await get_customer_by_id(session, customer_id, user_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado ou não pertence ao usuário.",
        )
    return customer


async def update_customer_service(
    session: AsyncSession, customer_id: int, customer_data: CustomerUpdate, user_id: int
) -> Customer:
    customer = await get_customer_by_id_service(session, customer_id, user_id)

    if (
        customer_data.company_cnpj
        and customer_data.company_cnpj != customer.company_cnpj
    ):
        existing_customer = await get_customer_by_cnpj(
            session, customer_data.company_cnpj
        )
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente cadastrado com este CNPJ.",
            )

    for key, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)

    return await update_customer(session, customer)


async def delete_customer_service(
    session: AsyncSession, customer_id: int, user_id: int
):
    customer = await get_customer_by_id_service(session, customer_id, user_id)
    await delete_customer(session, customer)
