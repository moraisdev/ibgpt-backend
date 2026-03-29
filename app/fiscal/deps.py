from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.config import settings
from app.fiscal.db import get_fiscal_session
from app.fiscal.models.ibgpt_user import get_user_by_email_sync

_bearer = HTTPBearer(auto_error=False)


class FiscalUser:
    def __init__(self, user_id: int, email: str, cnpj: str, role: str):
        self.id = user_id
        self.email = email
        self.cnpj = cnpj
        self.role = role
        self.escritorio_id = None


DBSession = Annotated[Session, Depends(get_fiscal_session)]


def get_current_fiscal_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
    db: Session = Depends(get_fiscal_session),
) -> FiscalUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Token ausente")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        user_data = get_user_by_email_sync(db, email)
        if not user_data:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return FiscalUser(
            user_id=user_data["id"],
            email=email,
            cnpj=user_data["cnpj"],
            role=user_data["role"],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


CurrentUser = Annotated[FiscalUser, Depends(get_current_fiscal_user)]


def get_empresa_do_escritorio(cnpj: str, user: FiscalUser, db: Session):
    from app.fiscal.models.company import Company

    empresa = db.query(Company).filter(Company.cnpj == cnpj).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {cnpj} não encontrada")
    return empresa
