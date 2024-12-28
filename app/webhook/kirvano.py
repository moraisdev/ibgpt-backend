from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.repositories.auth import get_user_by_email

router = APIRouter()


@router.post("/kirvano")
async def kirvano_webhook(
    token: str = Header(..., description="Seu token para autenticar o webhook"),
    body: dict = Body(..., description="JSON enviado pelo gateway"),
    session: AsyncSession = Depends(get_async_session),
):

    if token != "ADF3BE42503B04ED00DA809AA880FC8F":
        raise HTTPException(status_code=401, detail="Token inválido para Webhook")

    email = body.get("customer", {}).get("email")
    if not email:
        raise HTTPException(400, "Não existe 'email' em body['customer']")

    event = body.get("event")
    status = body.get("status")

    user = await get_user_by_email(session, email)
    if not user:
        raise HTTPException(404, f"Usuário com email={email} não encontrado")

    if event in ["SALE_APPROVED", "SUBSCRIPTION_RENEWED"]:
        user.subscription_status = "APPROVED"
    elif event in ["SALE_REFUNDED", "SUBSCRIPTION_CANCELED", "SALE_CHARGEBACK"]:
        user.subscription_status = status
    elif event == "SUBSCRIPTION_EXPIRED":
        user.subscription_status = "PENDING"
    else:
        user.subscription_status = status or event or "UNKNOWN"

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "detail": "Webhook processado",
        "subscription_status": user.subscription_status,
    }
