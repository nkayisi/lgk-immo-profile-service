from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from core.database import get_db
from core.security import generate_client_id, generate_secret_key, hash_secret
from models.api_key import APIKeyDB

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class CreateAPIKeyRequest(BaseModel):
    service_name: str


class APIKeyResponse(BaseModel):
    client_id: str
    secret_key: str
    service_name: str
    message: str = "Store the secret_key securely. It won't be shown again."


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key pair for a service."""
    client_id = generate_client_id()
    secret_key = generate_secret_key()
    secret_hash = hash_secret(secret_key)

    api_key = APIKeyDB(
        client_id=client_id,
        secret_key_hash=secret_hash,
        service_name=request.service_name
    )

    db.add(api_key)
    await db.commit()

    return APIKeyResponse(
        client_id=client_id,
        secret_key=secret_key,
        service_name=request.service_name
    )
