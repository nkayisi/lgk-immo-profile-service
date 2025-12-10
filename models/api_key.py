"""
Modèle APIKey pour l'authentification des services.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from core.database import Base


class APIKeyDB(Base):
    """
    Table des clés API pour l'authentification inter-services.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(String(100), unique=True, index=True, nullable=False)
    secret_key_hash = Column(String(255), nullable=False)
    service_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<APIKey(id={self.id}, service={self.service_name}, active={self.is_active})>"
