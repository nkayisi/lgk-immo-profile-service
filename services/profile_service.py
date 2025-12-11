"""
Service métier pour la gestion des profils.
Contient la logique métier et les validations.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from models.profile_base import Profile
from models.profile_document import ProfileDocument
from models.profile_verification import ProfileVerification
from models.enums import ProfileType, Gender, DocumentType, VerificationStatus
from repositories.profile_repository import (
    profile_repository,
    document_repository,
    verification_repository,
)
from gql_schema.profile_types import (
    ProfileUnion,
    IndividualProfileType,
    BusinessProfileType,
    ProfileDocumentType,
    ProfileVerificationType,
    ProfileTypeGQL,
    GenderGQL,
    DocumentTypeGQL,
    VerificationStatusGQL,
)


class ProfileServiceError(Exception):
    """Exception personnalisée pour les erreurs du service Profile."""
    pass


class ProfileService:
    """Service pour la gestion des profils utilisateurs."""

    # =========================================================================
    # CONVERSION DB -> GraphQL
    # =========================================================================

    @staticmethod
    def _convert_document_to_gql(doc: ProfileDocument) -> ProfileDocumentType:
        """Convertit un document DB en type GraphQL."""
        return ProfileDocumentType(
            id=str(doc.id),
            profile_id=str(doc.profile_id),
            file_type=DocumentTypeGQL(doc.file_type.value),
            file_name=doc.file_name,
            url=doc.url,
            verified=doc.verified,
            uploaded_at=doc.uploaded_at,
        )

    @staticmethod
    def _convert_verification_to_gql(verif: ProfileVerification) -> ProfileVerificationType:
        """Convertit une vérification DB en type GraphQL."""
        return ProfileVerificationType(
            id=str(verif.id),
            profile_id=str(verif.profile_id),
            status=VerificationStatusGQL(verif.status.value),
            reviewed_by=verif.reviewed_by,
            reviewed_at=verif.reviewed_at,
            notes=verif.notes,
            created_at=verif.created_at,
        )

    def _convert_profile_to_gql(self, profile: Profile) -> ProfileUnion:
        """Convertit un profil DB en type GraphQL approprié."""
        documents = [self._convert_document_to_gql(d) for d in (profile.documents or [])]
        verifications = [self._convert_verification_to_gql(v) for v in (profile.verifications or [])]

        base_data = {
            "id": str(profile.id),
            "external_user_id": str(profile.external_user_id),
            "profile_type": ProfileTypeGQL(profile.profile_type.value),
            "phone_number": profile.phone_number,
            "country": profile.country,
            "city": profile.city,
            "address": profile.address,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "documents": documents,
            "verifications": verifications,
        }

        if profile.profile_type == ProfileType.INDIVIDUAL and profile.individual_profile:
            ind = profile.individual_profile
            gender_gql = GenderGQL(ind.gender.value) if ind.gender else None
            return IndividualProfileType(
                **base_data,
                first_name=ind.first_name,
                last_name=ind.last_name,
                date_of_birth=ind.date_of_birth,
                gender=gender_gql,
                national_id_number=ind.national_id_number,
            )
        elif profile.profile_type == ProfileType.BUSINESS and profile.business_profile:
            bus = profile.business_profile
            return BusinessProfileType(
                **base_data,
                business_name=bus.business_name,
                registration_number=bus.registration_number,
                tax_id=bus.tax_id,
                legal_representative_name=bus.legal_representative_name,
            )
        else:
            raise ProfileServiceError(f"Invalid profile type or missing sub-profile for profile {profile.id}")

    # =========================================================================
    # QUERIES
    # =========================================================================

    async def get_profile(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> Optional[ProfileUnion]:
        """Récupère un profil par son ID."""
        profile = await profile_repository.get_by_id_with_details(db, profile_id)
        if not profile:
            return None
        return self._convert_profile_to_gql(profile)

    async def get_profile_by_external_user_id(
        self,
        db: AsyncSession,
        external_user_id: str
    ) -> Optional[ProfileUnion]:
        """Récupère un profil par l'ID utilisateur externe."""
        profile = await profile_repository.get_by_external_user_id(db, external_user_id)
        if not profile:
            return None
        return self._convert_profile_to_gql(profile)

    async def get_profiles(
        self,
        db: AsyncSession,
        profile_type: Optional[ProfileTypeGQL] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        verification_status: Optional[VerificationStatusGQL] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[ProfileUnion], int, bool]:
        """Récupère les profils avec filtres et pagination."""
        # Conversion des enums GraphQL vers DB
        db_profile_type = ProfileType(profile_type.value) if profile_type else None
        db_verification_status = VerificationStatus(verification_status.value) if verification_status else None

        profiles, total_count = await profile_repository.get_profiles_filtered(
            db=db,
            profile_type=db_profile_type,
            country=country,
            city=city,
            verification_status=db_verification_status,
            search=search,
            limit=limit,
            offset=offset,
        )

        gql_profiles = [self._convert_profile_to_gql(p) for p in profiles]
        has_next_page = (offset + limit) < total_count

        return gql_profiles, total_count, has_next_page

    # =========================================================================
    # MUTATIONS - Création
    # =========================================================================

    async def create_individual_profile(
        self,
        db: AsyncSession,
        external_user_id: str,
        phone_number: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        address: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        gender: Optional[GenderGQL] = None,
        national_id_number: Optional[str] = None,
    ) -> ProfileUnion:
        """Crée un nouveau profil individuel."""
        # Vérifier si un profil existe déjà pour cet utilisateur
        existing = await profile_repository.get_by_external_user_id(db, external_user_id)
        if existing:
            raise ProfileServiceError(f"A profile already exists for user {external_user_id}")

        # Conversion du genre
        db_gender = Gender(gender.value) if gender else None

        profile = await profile_repository.create_individual_profile(
            db=db,
            external_user_id=external_user_id,
            phone_number=phone_number,
            country=country,
            city=city,
            address=address,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=db_gender,
            national_id_number=national_id_number,
        )
        return self._convert_profile_to_gql(profile)

    async def create_business_profile(
        self,
        db: AsyncSession,
        external_user_id: str,
        business_name: str,
        phone_number: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        address: Optional[str] = None,
        registration_number: Optional[str] = None,
        tax_id: Optional[str] = None,
        legal_representative_name: Optional[str] = None,
    ) -> ProfileUnion:
        """Crée un nouveau profil entreprise."""
        # Vérifier si un profil existe déjà pour cet utilisateur
        existing = await profile_repository.get_by_external_user_id(db, external_user_id)
        if existing:
            raise ProfileServiceError(f"A profile already exists for user {external_user_id}")

        if not business_name:
            raise ProfileServiceError("Business name is required for business profiles")

        profile = await profile_repository.create_business_profile(
            db=db,
            external_user_id=external_user_id,
            business_name=business_name,
            phone_number=phone_number,
            country=country,
            city=city,
            address=address,
            registration_number=registration_number,
            tax_id=tax_id,
            legal_representative_name=legal_representative_name,
        )
        return self._convert_profile_to_gql(profile)

    # =========================================================================
    # MUTATIONS - Mise à jour
    # =========================================================================

    async def update_individual_profile(
        self,
        db: AsyncSession,
        profile_id: UUID,
        **kwargs
    ) -> Optional[ProfileUnion]:
        """Met à jour un profil individuel."""
        # Filtrer les valeurs UNSET de Strawberry
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Conversion du genre si présent
        if "gender" in filtered_kwargs and filtered_kwargs["gender"]:
            filtered_kwargs["gender"] = Gender(filtered_kwargs["gender"].value)

        profile = await profile_repository.update_individual_profile(
            db=db,
            profile_id=profile_id,
            **filtered_kwargs
        )
        if not profile:
            return None
        return self._convert_profile_to_gql(profile)

    async def update_business_profile(
        self,
        db: AsyncSession,
        profile_id: UUID,
        **kwargs
    ) -> Optional[ProfileUnion]:
        """Met à jour un profil entreprise."""
        # Filtrer les valeurs UNSET de Strawberry
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        profile = await profile_repository.update_business_profile(
            db=db,
            profile_id=profile_id,
            **filtered_kwargs
        )
        if not profile:
            return None
        return self._convert_profile_to_gql(profile)

    async def delete_profile(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> bool:
        """Supprime un profil."""
        return await profile_repository.delete(db, profile_id)

    # =========================================================================
    # DOCUMENTS
    # =========================================================================

    async def upload_document(
        self,
        db: AsyncSession,
        profile_id: UUID,
        file_type: DocumentTypeGQL,
        url: str,
        file_name: Optional[str] = None,
    ) -> ProfileDocumentType:
        """Ajoute un document à un profil."""
        # Vérifier que le profil existe
        profile = await profile_repository.get_by_id_with_details(db, profile_id)
        if not profile:
            raise ProfileServiceError(f"Profile {profile_id} not found")

        db_file_type = DocumentType(file_type.value)
        document = await document_repository.create_document(
            db=db,
            profile_id=profile_id,
            file_type=db_file_type,
            url=url,
            file_name=file_name,
        )
        return self._convert_document_to_gql(document)

    async def verify_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        verified: bool
    ) -> Optional[ProfileDocumentType]:
        """Vérifie ou invalide un document."""
        document = await document_repository.verify_document(db, document_id, verified)
        if not document:
            return None
        return self._convert_document_to_gql(document)

    async def get_profile_documents(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> List[ProfileDocumentType]:
        """Récupère tous les documents d'un profil."""
        documents = await document_repository.get_by_profile_id(db, profile_id)
        return [self._convert_document_to_gql(d) for d in documents]

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> bool:
        """Supprime un document."""
        return await document_repository.delete(db, document_id)

    # =========================================================================
    # VERIFICATION
    # =========================================================================

    async def verify_profile(
        self,
        db: AsyncSession,
        profile_id: UUID,
        status: VerificationStatusGQL,
        reviewed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> ProfileVerificationType:
        """Crée une nouvelle vérification pour un profil."""
        # Vérifier que le profil existe
        profile = await profile_repository.get_by_id_with_details(db, profile_id)
        if not profile:
            raise ProfileServiceError(f"Profile {profile_id} not found")

        db_status = VerificationStatus(status.value)
        verification = await verification_repository.create_verification(
            db=db,
            profile_id=profile_id,
            status=db_status,
            notes=notes,
        )

        # Si un reviewer est fourni, mettre à jour immédiatement
        if reviewed_by:
            verification = await verification_repository.update_verification(
                db=db,
                verification_id=verification.id,
                status=db_status,
                reviewed_by=reviewed_by,
                notes=notes,
            )

        return self._convert_verification_to_gql(verification)

    async def update_verification(
        self,
        db: AsyncSession,
        verification_id: UUID,
        status: VerificationStatusGQL,
        reviewed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[ProfileVerificationType]:
        """Met à jour une vérification existante."""
        db_status = VerificationStatus(status.value)
        verification = await verification_repository.update_verification(
            db=db,
            verification_id=verification_id,
            status=db_status,
            reviewed_by=reviewed_by,
            notes=notes,
        )
        if not verification:
            return None
        return self._convert_verification_to_gql(verification)

    async def get_profile_verifications(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> List[ProfileVerificationType]:
        """Récupère l'historique des vérifications d'un profil."""
        verifications = await verification_repository.get_by_profile_id(db, profile_id)
        return [self._convert_verification_to_gql(v) for v in verifications]

    async def get_latest_verification(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> Optional[ProfileVerificationType]:
        """Récupère la dernière vérification d'un profil."""
        verification = await verification_repository.get_latest_by_profile_id(db, profile_id)
        if not verification:
            return None
        return self._convert_verification_to_gql(verification)


# Instance singleton
profile_service = ProfileService()
