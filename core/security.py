import secrets
import bcrypt
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import API_KEY_HEADER, API_SECRET_HEADER
from core.database import get_db
from models.api_key import APIKeyDB

api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)
api_secret_header = APIKeyHeader(name=API_SECRET_HEADER, auto_error=False)


def generate_client_id() -> str:
    return f"cli_{secrets.token_hex(16)}"


def generate_secret_key() -> str:
    return f"sk_{secrets.token_hex(32)}"


def hash_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    return bcrypt.checkpw(plain_secret.encode(), hashed_secret.encode())


async def verify_api_key(
    client_id: str = Security(api_key_header),
    secret_key: str = Security(api_secret_header),
    db: AsyncSession = Depends(get_db)
) -> APIKeyDB:
    if not client_id or not secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API credentials",
            headers={"WWW-Authenticate": "API-Key"},
        )

    result = await db.execute(
        select(APIKeyDB).where(
            APIKeyDB.client_id == client_id,
            APIKeyDB.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key or not verify_secret(secret_key, api_key.secret_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API credentials",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return api_key
