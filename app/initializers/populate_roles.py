from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.role import Role


async def populate_roles(session: AsyncSession):
    result = await session.execute(select(Role))
    existing_roles = {role.id for role in result.scalars()}

    roles = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "user_manager"},
        {"id": 3, "name": "user"},
    ]

    for role_data in roles:
        if role_data["id"] not in existing_roles:
            session.add(Role(**role_data))

    await session.commit()
    print("Tabela de roles populada com sucesso.")
