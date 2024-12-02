from app.services.auth import get_current_user
from app.schemas.auth import UserResponse
from fastapi import APIRouter, Depends
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=UserResponse)
async def get_user_data(current_user: User = Depends(get_current_user)):
    return current_user
