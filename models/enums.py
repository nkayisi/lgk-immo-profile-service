"""
Enums partagés pour le module Profile.
"""
import enum


class ProfileType(str, enum.Enum):
    """Type de profil utilisateur."""
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"


class Gender(str, enum.Enum):
    """Genre de l'utilisateur."""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class DocumentType(str, enum.Enum):
    """Type de document uploadé."""
    ID_CARD = "ID_CARD"
    PASSPORT = "PASSPORT"
    COMPANY_REGISTRATION = "COMPANY_REGISTRATION"
    TAX_CERTIFICATE = "TAX_CERTIFICATE"
    PROFILE_PHOTO = "PROFILE_PHOTO"
    PROOF_OF_ADDRESS = "PROOF_OF_ADDRESS"
    OTHER = "OTHER"


class VerificationStatus(str, enum.Enum):
    """Statut de vérification du profil."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
