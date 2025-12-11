import ssl as ssl_module
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import DATABASE_URL

# Paramètres non supportés par asyncpg (spécifiques à libpq/psycopg2)
UNSUPPORTED_PARAMS = {
    'sslmode', 'channel_binding', 'connect_timeout', 'application_name',
    'options', 'keepalives', 'keepalives_idle', 'keepalives_interval',
    'keepalives_count', 'sslcert', 'sslkey', 'sslrootcert', 'sslcrl',
    'requirepeer', 'krbsrvname', 'gsslib', 'service', 'target_session_attrs'
}

def get_async_database_url(url: str) -> tuple[str, dict]:
    """
    Convertit une URL PostgreSQL standard en URL asyncpg compatible.
    Retourne (url_nettoyée, connect_args)
    """
    connect_args = {}
    
    # Convertir le scheme
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Parser l'URL
    parsed = urlparse(url)
    
    # Extraire et filtrer les paramètres de query
    if parsed.query:
        params = parse_qs(parsed.query)
        
        # Vérifier si SSL est requis
        if 'sslmode' in params:
            sslmode = params['sslmode'][0]
            if sslmode in ('require', 'verify-ca', 'verify-full'):
                ssl_context = ssl_module.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl_module.CERT_NONE
                connect_args['ssl'] = ssl_context
        
        # Filtrer les paramètres non supportés
        filtered_params = {
            k: v[0] if len(v) == 1 else v 
            for k, v in params.items() 
            if k not in UNSUPPORTED_PARAMS
        }
        
        # Reconstruire l'URL sans les paramètres non supportés
        new_query = urlencode(filtered_params, doseq=True) if filtered_params else ''
        parsed = parsed._replace(query=new_query)
    
    return urlunparse(parsed), connect_args

ASYNC_DATABASE_URL, connect_args = get_async_database_url(DATABASE_URL)

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
