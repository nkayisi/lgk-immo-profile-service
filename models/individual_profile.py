"""
Modèle IndividualProfile - Table spécifique pour les profils individuels (TPT Pattern).
"""
from datetime import date
from sqlalchemy import Column, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.enums import Gender


class IndividualProfile(Base):
    """
    Table des profils individuels (particuliers).
    Hérite de Profile via TPT (Table Per Type).
    """
    __tablename__ = "individual_profiles"

    id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True
    )
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    national_id_number = Column(String(50), nullable=True, unique=True)

    # Relation inverse
    profile = relationship("Profile", back_populates="individual_profile")

    def __repr__(self):
        return f"<IndividualProfile(id={self.id}, name={self.first_name} {self.last_name})>"
