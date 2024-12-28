from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import SecuritySchemeType
from app.db.database import engine
from app.models.base import Base
import logging
from typing import AsyncGenerator
from fastapi.openapi.utils import get_openapi
from app.initializers.populate_roles import populate_roles
from typing import AsyncGenerator
from app.db.database import get_async_session

from app.routers.location import router as location_router
from app.routers.auth import router as auth_router
from app.routers.customer import router as customer_router
from app.routers.user import router as user_router
from app.routers.offer import router as offer_router
from app.webhook.kirvano import router as kirvano_router
from app.routers.chat import router as chat_router
from app.middleware.standardize_middleware import StandardizeMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def lifespan(app: FastAPI) -> AsyncGenerator:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tabelas criadas com sucesso.")

    session_generator = get_async_session()
    session = await session_generator.__anext__()
    try:
        await populate_roles(session)
    finally:
        await session_generator.aclose()

    yield

    await engine.dispose()
    logger.info("Conexão com o banco de dados foi fechada.")


app = FastAPI(lifespan=lifespan)
# app.add_middleware(StandardizeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IBGPT Backend",
        version="1.0.0",
        description="Descrição da API com autenticação JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": SecuritySchemeType.http.value,
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
app.include_router(customer_router, prefix="/customers", tags=["Clientes"])
app.include_router(location_router, prefix="/location", tags=["Localidade"])
app.include_router(user_router, prefix="/users", tags=["Usuarios"])
app.include_router(offer_router, prefix="/offers", tags=["Ofertas"])
app.include_router(kirvano_router, prefix="/webhook", tags=["Webhooks"])
app.include_router(chat_router, prefix="/ia", tags=["Chat IA"])
