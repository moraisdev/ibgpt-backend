from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.services.customer import (
    create_customer_service,
    get_customer_by_id_service,
    get_all_customers_service,
    update_customer_service,
    delete_customer_service,
)
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_customer_service(session, customer, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar o cliente: {str(e)}",
        )


@router.get("/", response_model=list[CustomerResponse])
async def get_all_customers(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await get_all_customers_service(session, current_user.id)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer_by_id(
    customer_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    customer = await get_customer_by_id_service(session, customer_id, current_user.id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado ou não pertence ao usuário.",
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_customer_service(
            session, customer_id, customer, current_user.id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar o cliente: {str(e)}",
        )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_customer_service(session, customer_id, current_user.id)
    except HTTPException as e:
        raise e
