"""
Types GraphQL Strawberry pour le module Profile.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List, Annotated
import strawberry
from enum import Enum


# ============================================================================
# ENUMS GraphQL
# ============================================================================

@strawberry.enum
class ProfileTypeGQL(Enum):
    """Type de profil utilisateur."""
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"


@strawberry.enum
class GenderGQL(Enum):
    """Genre de l'utilisateur."""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


@strawberry.enum
class DocumentTypeGQL(Enum):
    """Type de document uploadé."""
    ID_CARD = "ID_CARD"
    PASSPORT = "PASSPORT"
    COMPANY_REGISTRATION = "COMPANY_REGISTRATION"
    TAX_CERTIFICATE = "TAX_CERTIFICATE"
    PROFILE_PHOTO = "PROFILE_PHOTO"
    PROOF_OF_ADDRESS = "PROOF_OF_ADDRESS"
    OTHER = "OTHER"


@strawberry.enum
class VerificationStatusGQL(Enum):
    """Statut de vérification du profil."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ============================================================================
# TYPES GraphQL - Documents & Verification
# ============================================================================

@strawberry.type
class ProfileDocumentType:
    """Document associé à un profil."""
    id: strawberry.ID
    profile_id: strawberry.ID
    file_type: DocumentTypeGQL
    file_name: Optional[str]
    url: str
    verified: bool
    uploaded_at: datetime


@strawberry.type
class ProfileVerificationType:
    """Historique de vérification d'un profil."""
    id: strawberry.ID
    profile_id: strawberry.ID
    status: VerificationStatusGQL
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime


# ============================================================================
# INTERFACE GraphQL - Profile Base
# ============================================================================

@strawberry.interface
class ProfileInterface:
    """Interface commune pour tous les types de profils."""
    id: strawberry.ID
    external_user_id: strawberry.ID
    profile_type: ProfileTypeGQL
    phone_number: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime
    documents: List[ProfileDocumentType]
    verifications: List[ProfileVerificationType]


# ============================================================================
# TYPES GraphQL - Profils spécifiques
# ============================================================================

@strawberry.type
class IndividualProfileType(ProfileInterface):
    """Profil individuel (particulier)."""
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[GenderGQL]
    national_id_number: Optional[str]

    @strawberry.field
    def full_name(self) -> Optional[str]:
        """Retourne le nom complet."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name


@strawberry.type
class BusinessProfileType(ProfileInterface):
    """Profil entreprise (professionnel)."""
    business_name: str
    registration_number: Optional[str]
    tax_id: Optional[str]
    legal_representative_name: Optional[str]


# ============================================================================
# UNION GraphQL - Pour les queries polymorphiques
# ============================================================================

ProfileUnion = Annotated[
    IndividualProfileType | BusinessProfileType,
    strawberry.union("ProfileUnion")
]


# ============================================================================
# TYPES GraphQL - Réponses
# ============================================================================

@strawberry.type
class ProfileResponse:
    """Réponse standard pour les opérations sur les profils."""
    success: bool
    message: str
    profile: Optional[ProfileUnion] = None


@strawberry.type
class DocumentResponse:
    """Réponse pour les opérations sur les documents."""
    success: bool
    message: str
    document: Optional[ProfileDocumentType] = None


@strawberry.type
class VerificationResponse:
    """Réponse pour les opérations de vérification."""
    success: bool
    message: str
    verification: Optional[ProfileVerificationType] = None


@strawberry.type
class ProfileListResponse:
    """Réponse paginée pour la liste des profils."""
    profiles: List[ProfileUnion]
    total_count: int
    has_next_page: bool
