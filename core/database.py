from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import DATABASE_URL

# Convertir l'URL PostgreSQL standard en URL asyncpg
def get_async_database_url(url: str) -> str:
    """Convertit postgresql:// en postgresql+asyncpg:// et sslmode en ssl"""
    # Convertir le scheme
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # asyncpg utilise 'ssl' au lieu de 'sslmode'
    # Convertir sslmode=require en ssl=require
    url = url.replace("sslmode=", "ssl=")
    
    return url

ASYNC_DATABASE_URL = get_async_database_url(DATABASE_URL)

# Configuration SSL pour asyncpg
connect_args = {}
if "ssl=" in ASYNC_DATABASE_URL or "sslmode=" in DATABASE_URL:
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context
    # Retirer le paramètre ssl de l'URL car on le passe via connect_args
    if "?" in ASYNC_DATABASE_URL:
        base_url, params = ASYNC_DATABASE_URL.split("?", 1)
        params_list = [p for p in params.split("&") if not p.startswith("ssl=")]
        ASYNC_DATABASE_URL = base_url + ("?" + "&".join(params_list) if params_list else "")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, connect_args=connect_args)

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
