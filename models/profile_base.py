"""
Modèle de base Profile - Table principale (TPT Pattern).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.enums import ProfileType


class Profile(Base):
    """
    Table principale des profils.
    Contient les champs communs à tous les types de profils.
    """
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    external_user_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="Référence vers User dans Auth Service")
    profile_type = Column(SQLEnum(ProfileType), nullable=False)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    individual_profile = relationship(
        "IndividualProfile",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )
    business_profile = relationship(
        "BusinessProfile",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )
    documents = relationship(
        "ProfileDocument",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    verifications = relationship(
        "ProfileVerification",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Profile(id={self.id}, type={self.profile_type}, external_user_id={self.external_user_id})>"
