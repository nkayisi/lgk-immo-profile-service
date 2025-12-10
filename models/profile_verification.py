"""
Modèle ProfileVerification - Historique de vérification des profils.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.enums import VerificationStatus


class ProfileVerification(Base):
    """
    Table de l'historique de vérification des profils.
    Permet de suivre les différentes étapes de validation KYC.
    """
    __tablename__ = "profile_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status = Column(SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING)
    reviewed_by = Column(String(255), nullable=True, comment="ID ou nom du reviewer")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relation inverse
    profile = relationship("Profile", back_populates="verifications")

    def __repr__(self):
        return f"<ProfileVerification(id={self.id}, status={self.status})>"
