"""
Modèle ProfileDocument - Documents associés aux profils.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.enums import DocumentType


class ProfileDocument(Base):
    """
    Table des documents associés aux profils.
    Permet de stocker les pièces justificatives (ID, certificats, etc.).
    """
    __tablename__ = "profile_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=True)
    url = Column(String(1000), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relation inverse
    profile = relationship("Profile", back_populates="documents")

    def __repr__(self):
        return f"<ProfileDocument(id={self.id}, type={self.file_type}, verified={self.verified})>"
