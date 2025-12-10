from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialise la base de données et crée toutes les tables."""
    # Import des modèles pour qu'ils soient enregistrés dans Base.metadata
    from models.profile_base import Profile
    from models.individual_profile import IndividualProfile
    from models.business_profile import BusinessProfile
    from models.profile_document import ProfileDocument
    from models.profile_verification import ProfileVerification
    from models.api_key import APIKeyDB
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
