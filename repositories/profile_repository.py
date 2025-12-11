"""
Repositories pour les opérations sur les profils.
Contient le BaseRepository et les repositories spécialisés.
"""
from typing import TypeVar, Generic, Type, Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from core.database import Base

from models.profile_base import Profile
from models.individual_profile import IndividualProfile
from models.business_profile import BusinessProfile
from models.profile_document import ProfileDocument
from models.profile_verification import ProfileVerification
from models.enums import ProfileType, VerificationStatus

ModelType = TypeVar("ModelType", bound=Base)


# =============================================================================
# BASE REPOSITORY
# =============================================================================

class BaseRepository(Generic[ModelType]):
    """Repository générique avec opérations CRUD de base."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self,
        db: AsyncSession,
        id: UUID,
        load_relations: List[str] = None
    ) -> Optional[ModelType]:
        """Récupère une entité par son ID."""
        query = select(self.model).where(self.model.id == id)
        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        load_relations: List[str] = None
    ) -> List[ModelType]:
        """Récupère toutes les entités avec pagination."""
        query = select(self.model).limit(limit).offset(offset)
        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """Compte le nombre total d'entités."""
        result = await db.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        """Crée une nouvelle entité."""
        instance = self.model(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(
        self,
        db: AsyncSession,
        id: UUID,
        **kwargs
    ) -> Optional[ModelType]:
        """Met à jour une entité existante."""
        instance = await self.get_by_id(db, id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Supprime une entité."""
        instance = await self.get_by_id(db, id)
        if not instance:
            return False
        await db.delete(instance)
        await db.commit()
        return True


# =============================================================================
# PROFILE REPOSITORY
# =============================================================================

class ProfileRepository(BaseRepository[Profile]):
    """Repository pour les profils."""

    def __init__(self):
        super().__init__(Profile)

    async def get_by_id_with_details(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> Optional[Profile]:
        """Récupère un profil avec toutes ses relations."""
        query = (
            select(Profile)
            .where(Profile.id == profile_id)
            .options(
                selectinload(Profile.individual_profile),
                selectinload(Profile.business_profile),
                selectinload(Profile.documents),
                selectinload(Profile.verifications),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_external_user_id(
        self,
        db: AsyncSession,
        external_user_id: str
    ) -> Optional[Profile]:
        """Récupère un profil par l'ID utilisateur externe."""
        query = (
            select(Profile)
            .where(Profile.external_user_id == external_user_id)
            .options(
                selectinload(Profile.individual_profile),
                selectinload(Profile.business_profile),
                selectinload(Profile.documents),
                selectinload(Profile.verifications),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_profiles_filtered(
        self,
        db: AsyncSession,
        profile_type: Optional[ProfileType] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        verification_status: Optional[VerificationStatus] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Profile], int]:
        """Récupère les profils avec filtres et pagination."""
        query = select(Profile).options(
            selectinload(Profile.individual_profile),
            selectinload(Profile.business_profile),
            selectinload(Profile.documents),
            selectinload(Profile.verifications),
        )
        count_query = select(func.count(Profile.id))

        # Appliquer les filtres
        if profile_type:
            query = query.where(Profile.profile_type == profile_type)
            count_query = count_query.where(Profile.profile_type == profile_type)

        if country:
            query = query.where(Profile.country.ilike(f"%{country}%"))
            count_query = count_query.where(Profile.country.ilike(f"%{country}%"))

        if city:
            query = query.where(Profile.city.ilike(f"%{city}%"))
            count_query = count_query.where(Profile.city.ilike(f"%{city}%"))

        if verification_status:
            subquery = (
                select(ProfileVerification.profile_id)
                .where(ProfileVerification.status == verification_status)
                .distinct()
            )
            query = query.where(Profile.id.in_(subquery))
            count_query = count_query.where(Profile.id.in_(subquery))

        if search:
            search_filter = or_(
                Profile.phone_number.ilike(f"%{search}%"),
                Profile.address.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Pagination
        query = query.order_by(Profile.created_at.desc()).limit(limit).offset(offset)

        # Exécution
        result = await db.execute(query)
        profiles = list(result.scalars().all())

        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()

        return profiles, total_count

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
        date_of_birth=None,
        gender=None,
        national_id_number: Optional[str] = None,
    ) -> Profile:
        """Crée un profil individuel complet."""
        profile = Profile(
            external_user_id=external_user_id,
            profile_type=ProfileType.INDIVIDUAL,
            phone_number=phone_number,
            country=country,
            city=city,
            address=address,
        )
        db.add(profile)
        await db.flush()

        individual = IndividualProfile(
            id=profile.id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            national_id_number=national_id_number,
        )
        db.add(individual)

        verification = ProfileVerification(
            profile_id=profile.id,
            status=VerificationStatus.PENDING,
        )
        db.add(verification)

        await db.commit()
        return await self.get_by_id_with_details(db, profile.id)

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
    ) -> Profile:
        """Crée un profil entreprise complet."""
        profile = Profile(
            external_user_id=external_user_id,
            profile_type=ProfileType.BUSINESS,
            phone_number=phone_number,
            country=country,
            city=city,
            address=address,
        )
        db.add(profile)
        await db.flush()

        business = BusinessProfile(
            id=profile.id,
            business_name=business_name,
            registration_number=registration_number,
            tax_id=tax_id,
            legal_representative_name=legal_representative_name,
        )
        db.add(business)

        verification = ProfileVerification(
            profile_id=profile.id,
            status=VerificationStatus.PENDING,
        )
        db.add(verification)

        await db.commit()
        return await self.get_by_id_with_details(db, profile.id)

    async def update_individual_profile(
        self,
        db: AsyncSession,
        profile_id: UUID,
        **kwargs
    ) -> Optional[Profile]:
        """Met à jour un profil individuel."""
        profile = await self.get_by_id_with_details(db, profile_id)
        if not profile or profile.profile_type != ProfileType.INDIVIDUAL:
            return None

        base_fields = ["phone_number", "country", "city", "address"]
        for field in base_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(profile, field, kwargs[field])

        individual_fields = ["first_name", "last_name", "date_of_birth", "gender", "national_id_number"]
        if profile.individual_profile:
            for field in individual_fields:
                if field in kwargs and kwargs[field] is not None:
                    setattr(profile.individual_profile, field, kwargs[field])

        await db.commit()
        return await self.get_by_id_with_details(db, profile_id)

    async def update_business_profile(
        self,
        db: AsyncSession,
        profile_id: UUID,
        **kwargs
    ) -> Optional[Profile]:
        """Met à jour un profil entreprise."""
        profile = await self.get_by_id_with_details(db, profile_id)
        if not profile or profile.profile_type != ProfileType.BUSINESS:
            return None

        base_fields = ["phone_number", "country", "city", "address"]
        for field in base_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(profile, field, kwargs[field])

        business_fields = ["business_name", "registration_number", "tax_id", "legal_representative_name"]
        if profile.business_profile:
            for field in business_fields:
                if field in kwargs and kwargs[field] is not None:
                    setattr(profile.business_profile, field, kwargs[field])

        await db.commit()
        return await self.get_by_id_with_details(db, profile_id)


# =============================================================================
# DOCUMENT REPOSITORY
# =============================================================================

class DocumentRepository(BaseRepository[ProfileDocument]):
    """Repository pour les documents de profil."""

    def __init__(self):
        super().__init__(ProfileDocument)

    async def get_by_profile_id(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> List[ProfileDocument]:
        """Récupère tous les documents d'un profil."""
        query = select(ProfileDocument).where(ProfileDocument.profile_id == profile_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_document(
        self,
        db: AsyncSession,
        profile_id: UUID,
        file_type,
        url: str,
        file_name: Optional[str] = None,
    ) -> ProfileDocument:
        """Crée un nouveau document."""
        document = ProfileDocument(
            profile_id=profile_id,
            file_type=file_type,
            url=url,
            file_name=file_name,
            verified=False,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    async def verify_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        verified: bool
    ) -> Optional[ProfileDocument]:
        """Vérifie ou invalide un document."""
        document = await self.get_by_id(db, document_id)
        if not document:
            return None
        document.verified = verified
        await db.commit()
        await db.refresh(document)
        return document


# =============================================================================
# VERIFICATION REPOSITORY
# =============================================================================

class VerificationRepository(BaseRepository[ProfileVerification]):
    """Repository pour les vérifications de profil."""

    def __init__(self):
        super().__init__(ProfileVerification)

    async def get_by_profile_id(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> List[ProfileVerification]:
        """Récupère toutes les vérifications d'un profil."""
        query = (
            select(ProfileVerification)
            .where(ProfileVerification.profile_id == profile_id)
            .order_by(ProfileVerification.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_latest_by_profile_id(
        self,
        db: AsyncSession,
        profile_id: UUID
    ) -> Optional[ProfileVerification]:
        """Récupère la dernière vérification d'un profil."""
        query = (
            select(ProfileVerification)
            .where(ProfileVerification.profile_id == profile_id)
            .order_by(ProfileVerification.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_verification(
        self,
        db: AsyncSession,
        profile_id: UUID,
        status: VerificationStatus = VerificationStatus.PENDING,
        notes: Optional[str] = None,
    ) -> ProfileVerification:
        """Crée une nouvelle vérification."""
        verification = ProfileVerification(
            profile_id=profile_id,
            status=status,
            notes=notes,
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        return verification

    async def update_verification(
        self,
        db: AsyncSession,
        verification_id: UUID,
        status: VerificationStatus,
        reviewed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[ProfileVerification]:
        """Met à jour une vérification."""
        verification = await self.get_by_id(db, verification_id)
        if not verification:
            return None
        verification.status = status
        verification.reviewed_by = reviewed_by
        verification.reviewed_at = datetime.utcnow()
        if notes is not None:
            verification.notes = notes
        await db.commit()
        await db.refresh(verification)
        return verification


# =============================================================================
# INSTANCES SINGLETON
# =============================================================================

profile_repository = ProfileRepository()
document_repository = DocumentRepository()
verification_repository = VerificationRepository()
