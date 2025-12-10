"""
Queries GraphQL pour le module Profile.
"""
from typing import Optional, List
from uuid import UUID
import strawberry
from strawberry.types import Info

from gql_schema.profile_types import (
    ProfileUnion,
    ProfileListResponse,
    ProfileDocumentType,
    ProfileVerificationType,
    ProfileTypeGQL,
    VerificationStatusGQL,
)
from gql_schema.profile_inputs import ProfileFilterInput, PaginationInput
from services.profile_service import profile_service


@strawberry.type
class ProfileQuery:
    """Queries pour les profils."""

    @strawberry.field(description="Récupère un profil par son ID")
    async def profile(
        self,
        info: Info,
        id: strawberry.ID
    ) -> Optional[ProfileUnion]:
        """Récupère un profil par son ID."""
        db = info.context["db"]
        return await profile_service.get_profile(db, UUID(id))

    @strawberry.field(description="Récupère un profil par l'ID utilisateur externe")
    async def profile_by_user(
        self,
        info: Info,
        external_user_id: strawberry.ID
    ) -> Optional[ProfileUnion]:
        """Récupère un profil par l'ID utilisateur externe."""
        db = info.context["db"]
        return await profile_service.get_profile_by_external_user_id(db, UUID(external_user_id))

    @strawberry.field(description="Récupère les profils avec filtres et pagination")
    async def profiles(
        self,
        info: Info,
        filter: Optional[ProfileFilterInput] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> ProfileListResponse:
        """Récupère les profils avec filtres et pagination."""
        db = info.context["db"]

        # Valeurs par défaut
        limit = pagination.limit if pagination else 20
        offset = pagination.offset if pagination else 0

        # Extraction des filtres
        profile_type = filter.profile_type if filter else None
        country = filter.country if filter else None
        city = filter.city if filter else None
        verification_status = filter.verification_status if filter else None
        search = filter.search if filter else None

        profiles, total_count, has_next_page = await profile_service.get_profiles(
            db=db,
            profile_type=profile_type,
            country=country,
            city=city,
            verification_status=verification_status,
            search=search,
            limit=limit,
            offset=offset,
        )

        return ProfileListResponse(
            profiles=profiles,
            total_count=total_count,
            has_next_page=has_next_page,
        )

    @strawberry.field(description="Récupère les documents d'un profil")
    async def profile_documents(
        self,
        info: Info,
        profile_id: strawberry.ID
    ) -> List[ProfileDocumentType]:
        """Récupère les documents d'un profil."""
        db = info.context["db"]
        return await profile_service.get_profile_documents(db, UUID(profile_id))

    @strawberry.field(description="Récupère l'historique des vérifications d'un profil")
    async def profile_verifications(
        self,
        info: Info,
        profile_id: strawberry.ID
    ) -> List[ProfileVerificationType]:
        """Récupère l'historique des vérifications d'un profil."""
        db = info.context["db"]
        return await profile_service.get_profile_verifications(db, UUID(profile_id))

    @strawberry.field(description="Récupère la dernière vérification d'un profil")
    async def latest_verification(
        self,
        info: Info,
        profile_id: strawberry.ID
    ) -> Optional[ProfileVerificationType]:
        """Récupère la dernière vérification d'un profil."""
        db = info.context["db"]
        return await profile_service.get_latest_verification(db, UUID(profile_id))
