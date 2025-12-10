"""
Mutations GraphQL pour le module Profile.
"""
from typing import Optional
from uuid import UUID
import strawberry
from strawberry.types import Info

from gql_schema.profile_types import (
    ProfileResponse,
    DocumentResponse,
    VerificationResponse,
    ProfileUnion,
    ProfileDocumentType,
    ProfileVerificationType,
)
from gql_schema.profile_inputs import (
    CreateIndividualProfileInput,
    CreateBusinessProfileInput,
    UpdateIndividualProfileInput,
    UpdateBusinessProfileInput,
    UploadDocumentInput,
    VerifyDocumentInput,
    CreateVerificationInput,
    UpdateVerificationInput,
)
from services.profile_service import profile_service, ProfileServiceError


@strawberry.type
class ProfileMutation:
    """Mutations pour les profils."""

    # =========================================================================
    # CRÉATION DE PROFILS
    # =========================================================================

    @strawberry.mutation(description="Crée un nouveau profil individuel")
    async def create_individual_profile(
        self,
        info: Info,
        input: CreateIndividualProfileInput
    ) -> ProfileResponse:
        """Crée un nouveau profil individuel."""
        db = info.context["db"]
        try:
            profile = await profile_service.create_individual_profile(
                db=db,
                external_user_id=UUID(input.external_user_id),
                phone_number=input.phone_number,
                country=input.country,
                city=input.city,
                address=input.address,
                first_name=input.first_name,
                last_name=input.last_name,
                date_of_birth=input.date_of_birth,
                gender=input.gender,
                national_id_number=input.national_id_number,
            )
            return ProfileResponse(
                success=True,
                message="Individual profile created successfully",
                profile=profile,
            )
        except ProfileServiceError as e:
            return ProfileResponse(
                success=False,
                message=str(e),
                profile=None,
            )
        except Exception as e:
            return ProfileResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                profile=None,
            )

    @strawberry.mutation(description="Crée un nouveau profil entreprise")
    async def create_business_profile(
        self,
        info: Info,
        input: CreateBusinessProfileInput
    ) -> ProfileResponse:
        """Crée un nouveau profil entreprise."""
        db = info.context["db"]
        try:
            profile = await profile_service.create_business_profile(
                db=db,
                external_user_id=UUID(input.external_user_id),
                business_name=input.business_name,
                phone_number=input.phone_number,
                country=input.country,
                city=input.city,
                address=input.address,
                registration_number=input.registration_number,
                tax_id=input.tax_id,
                legal_representative_name=input.legal_representative_name,
            )
            return ProfileResponse(
                success=True,
                message="Business profile created successfully",
                profile=profile,
            )
        except ProfileServiceError as e:
            return ProfileResponse(
                success=False,
                message=str(e),
                profile=None,
            )
        except Exception as e:
            return ProfileResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                profile=None,
            )

    # =========================================================================
    # MISE À JOUR DE PROFILS
    # =========================================================================

    @strawberry.mutation(description="Met à jour un profil individuel")
    async def update_individual_profile(
        self,
        info: Info,
        id: strawberry.ID,
        input: UpdateIndividualProfileInput
    ) -> ProfileResponse:
        """Met à jour un profil individuel."""
        db = info.context["db"]
        try:
            # Extraire les champs non-UNSET
            update_data = {}
            for field in ["phone_number", "country", "city", "address",
                          "first_name", "last_name", "date_of_birth",
                          "gender", "national_id_number"]:
                value = getattr(input, field, strawberry.UNSET)
                if value is not strawberry.UNSET:
                    update_data[field] = value

            profile = await profile_service.update_individual_profile(
                db=db,
                profile_id=UUID(id),
                **update_data
            )
            if not profile:
                return ProfileResponse(
                    success=False,
                    message=f"Profile {id} not found or is not an individual profile",
                    profile=None,
                )
            return ProfileResponse(
                success=True,
                message="Individual profile updated successfully",
                profile=profile,
            )
        except Exception as e:
            return ProfileResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                profile=None,
            )

    @strawberry.mutation(description="Met à jour un profil entreprise")
    async def update_business_profile(
        self,
        info: Info,
        id: strawberry.ID,
        input: UpdateBusinessProfileInput
    ) -> ProfileResponse:
        """Met à jour un profil entreprise."""
        db = info.context["db"]
        try:
            # Extraire les champs non-UNSET
            update_data = {}
            for field in ["phone_number", "country", "city", "address",
                          "business_name", "registration_number",
                          "tax_id", "legal_representative_name"]:
                value = getattr(input, field, strawberry.UNSET)
                if value is not strawberry.UNSET:
                    update_data[field] = value

            profile = await profile_service.update_business_profile(
                db=db,
                profile_id=UUID(id),
                **update_data
            )
            if not profile:
                return ProfileResponse(
                    success=False,
                    message=f"Profile {id} not found or is not a business profile",
                    profile=None,
                )
            return ProfileResponse(
                success=True,
                message="Business profile updated successfully",
                profile=profile,
            )
        except Exception as e:
            return ProfileResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                profile=None,
            )

    @strawberry.mutation(description="Supprime un profil")
    async def delete_profile(
        self,
        info: Info,
        id: strawberry.ID
    ) -> ProfileResponse:
        """Supprime un profil."""
        db = info.context["db"]
        try:
            deleted = await profile_service.delete_profile(db, UUID(id))
            if not deleted:
                return ProfileResponse(
                    success=False,
                    message=f"Profile {id} not found",
                    profile=None,
                )
            return ProfileResponse(
                success=True,
                message="Profile deleted successfully",
                profile=None,
            )
        except Exception as e:
            return ProfileResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                profile=None,
            )

    # =========================================================================
    # DOCUMENTS
    # =========================================================================

    @strawberry.mutation(description="Upload un document pour un profil")
    async def upload_profile_document(
        self,
        info: Info,
        input: UploadDocumentInput
    ) -> DocumentResponse:
        """Upload un document pour un profil."""
        db = info.context["db"]
        try:
            document = await profile_service.upload_document(
                db=db,
                profile_id=UUID(input.profile_id),
                file_type=input.file_type,
                url=input.url,
                file_name=input.file_name,
            )
            return DocumentResponse(
                success=True,
                message="Document uploaded successfully",
                document=document,
            )
        except ProfileServiceError as e:
            return DocumentResponse(
                success=False,
                message=str(e),
                document=None,
            )
        except Exception as e:
            return DocumentResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                document=None,
            )

    @strawberry.mutation(description="Vérifie ou invalide un document")
    async def verify_document(
        self,
        info: Info,
        input: VerifyDocumentInput
    ) -> DocumentResponse:
        """Vérifie ou invalide un document."""
        db = info.context["db"]
        try:
            document = await profile_service.verify_document(
                db=db,
                document_id=UUID(input.document_id),
                verified=input.verified,
            )
            if not document:
                return DocumentResponse(
                    success=False,
                    message=f"Document {input.document_id} not found",
                    document=None,
                )
            status = "verified" if input.verified else "rejected"
            return DocumentResponse(
                success=True,
                message=f"Document {status} successfully",
                document=document,
            )
        except Exception as e:
            return DocumentResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                document=None,
            )

    @strawberry.mutation(description="Supprime un document")
    async def delete_document(
        self,
        info: Info,
        document_id: strawberry.ID
    ) -> DocumentResponse:
        """Supprime un document."""
        db = info.context["db"]
        try:
            deleted = await profile_service.delete_document(db, UUID(document_id))
            if not deleted:
                return DocumentResponse(
                    success=False,
                    message=f"Document {document_id} not found",
                    document=None,
                )
            return DocumentResponse(
                success=True,
                message="Document deleted successfully",
                document=None,
            )
        except Exception as e:
            return DocumentResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                document=None,
            )

    # =========================================================================
    # VÉRIFICATION
    # =========================================================================

    @strawberry.mutation(description="Vérifie un profil (change son statut de vérification)")
    async def verify_profile(
        self,
        info: Info,
        input: CreateVerificationInput
    ) -> VerificationResponse:
        """Crée une nouvelle vérification pour un profil."""
        db = info.context["db"]
        try:
            verification = await profile_service.verify_profile(
                db=db,
                profile_id=UUID(input.profile_id),
                status=input.status,
                notes=input.notes,
            )
            return VerificationResponse(
                success=True,
                message=f"Profile verification status set to {input.status.value}",
                verification=verification,
            )
        except ProfileServiceError as e:
            return VerificationResponse(
                success=False,
                message=str(e),
                verification=None,
            )
        except Exception as e:
            return VerificationResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                verification=None,
            )

    @strawberry.mutation(description="Met à jour une vérification existante")
    async def update_verification(
        self,
        info: Info,
        input: UpdateVerificationInput
    ) -> VerificationResponse:
        """Met à jour une vérification existante."""
        db = info.context["db"]
        try:
            verification = await profile_service.update_verification(
                db=db,
                verification_id=UUID(input.verification_id),
                status=input.status,
                reviewed_by=input.reviewed_by,
                notes=input.notes,
            )
            if not verification:
                return VerificationResponse(
                    success=False,
                    message=f"Verification {input.verification_id} not found",
                    verification=None,
                )
            return VerificationResponse(
                success=True,
                message="Verification updated successfully",
                verification=verification,
            )
        except Exception as e:
            return VerificationResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                verification=None,
            )
