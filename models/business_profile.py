"""
Modèle BusinessProfile - Table spécifique pour les profils entreprise (TPT Pattern).
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class BusinessProfile(Base):
    """
    Table des profils entreprise (professionnels).
    Hérite de Profile via TPT (Table Per Type).
    """
    __tablename__ = "business_profiles"

    id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True
    )
    business_name = Column(String(255), nullable=False)
    registration_number = Column(String(100), nullable=True, unique=True)
    tax_id = Column(String(100), nullable=True, unique=True)
    legal_representative_name = Column(String(200), nullable=True)

    # Relation inverse
    profile = relationship("Profile", back_populates="business_profile")

    def __repr__(self):
        return f"<BusinessProfile(id={self.id}, name={self.business_name})>"
