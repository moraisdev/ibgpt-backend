from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(session: AsyncSession, user_data: dict) -> User:
    new_user = User(**user_data)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return await get_user_by_id_with_role(session, new_user.id)


async def get_user_with_role_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).options(selectinload(User.role)).where(User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id_with_role(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalars().first()


async def update_password(session: AsyncSession, user: User, new_password: str) -> None:
    hashed_password = pwd_context.hash(new_password)
    user.password = hashed_password
    session.add(user)
    await session.commit()
    await session.refresh(user)
