from sqlalchemy import text
from sqlalchemy.orm import Session


def get_user_by_email_sync(db: Session, email: str) -> dict | None:
    row = db.execute(
        text(
            "SELECT u.id, u.cnpj, u.is_active, r.name as role_name "
            "FROM users u "
            "LEFT JOIN roles r ON r.id = u.role_id "
            "WHERE u.email = :email "
            "LIMIT 1"
        ),
        {"email": email},
    ).fetchone()

    if row is None or not row.is_active:
        return None

    return {
        "id": row.id,
        "cnpj": row.cnpj or "",
        "role": row.role_name or "user",
    }
