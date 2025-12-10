"""
Inputs GraphQL Strawberry pour le module Profile.
"""
import uuid
from datetime import date
from typing import Optional
import strawberry
from gql_schema.profile_types import (
    ProfileTypeGQL,
    GenderGQL,
    DocumentTypeGQL,
    VerificationStatusGQL,
)


# ============================================================================
# INPUTS - Création de profils
# ============================================================================

@strawberry.input
class CreateIndividualProfileInput:
    """Input pour créer un profil individuel."""
    external_user_id: strawberry.ID
    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    # Champs spécifiques Individual
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderGQL] = None
    national_id_number: Optional[str] = None


@strawberry.input
class CreateBusinessProfileInput:
    """Input pour créer un profil entreprise."""
    external_user_id: strawberry.ID
    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    # Champs spécifiques Business
    business_name: str
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    legal_representative_name: Optional[str] = None


# ============================================================================
# INPUTS - Mise à jour de profils
# ============================================================================

@strawberry.input
class UpdateProfileBaseInput:
    """Input pour mettre à jour les champs communs d'un profil."""
    phone_number: Optional[str] = strawberry.UNSET
    country: Optional[str] = strawberry.UNSET
    city: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET


@strawberry.input
class UpdateIndividualProfileInput:
    """Input pour mettre à jour un profil individuel."""
    # Champs communs
    phone_number: Optional[str] = strawberry.UNSET
    country: Optional[str] = strawberry.UNSET
    city: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET
    # Champs spécifiques Individual
    first_name: Optional[str] = strawberry.UNSET
    last_name: Optional[str] = strawberry.UNSET
    date_of_birth: Optional[date] = strawberry.UNSET
    gender: Optional[GenderGQL] = strawberry.UNSET
    national_id_number: Optional[str] = strawberry.UNSET


@strawberry.input
class UpdateBusinessProfileInput:
    """Input pour mettre à jour un profil entreprise."""
    # Champs communs
    phone_number: Optional[str] = strawberry.UNSET
    country: Optional[str] = strawberry.UNSET
    city: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET
    # Champs spécifiques Business
    business_name: Optional[str] = strawberry.UNSET
    registration_number: Optional[str] = strawberry.UNSET
    tax_id: Optional[str] = strawberry.UNSET
    legal_representative_name: Optional[str] = strawberry.UNSET


# ============================================================================
# INPUTS - Documents
# ============================================================================

@strawberry.input
class UploadDocumentInput:
    """Input pour uploader un document."""
    profile_id: strawberry.ID
    file_type: DocumentTypeGQL
    file_name: Optional[str] = None
    url: str


@strawberry.input
class VerifyDocumentInput:
    """Input pour vérifier un document."""
    document_id: strawberry.ID
    verified: bool


# ============================================================================
# INPUTS - Vérification
# ============================================================================

@strawberry.input
class CreateVerificationInput:
    """Input pour créer une vérification."""
    profile_id: strawberry.ID
    status: VerificationStatusGQL = VerificationStatusGQL.PENDING
    notes: Optional[str] = None


@strawberry.input
class UpdateVerificationInput:
    """Input pour mettre à jour une vérification."""
    verification_id: strawberry.ID
    status: VerificationStatusGQL
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None


# ============================================================================
# INPUTS - Filtres
# ============================================================================

@strawberry.input
class ProfileFilterInput:
    """Filtre pour la recherche de profils."""
    profile_type: Optional[ProfileTypeGQL] = None
    country: Optional[str] = None
    city: Optional[str] = None
    verification_status: Optional[VerificationStatusGQL] = None
    search: Optional[str] = None  # Recherche textuelle


@strawberry.input
class PaginationInput:
    """Input pour la pagination."""
    limit: int = 20
    offset: int = 0
