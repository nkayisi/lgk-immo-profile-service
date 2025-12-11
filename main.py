from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.graphql import router as graphql_router
from api.api_keys import router as api_keys_router
from core.database import init_db
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Profile Service",
    description="Microservice for managing user profiles",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Configuration CORS dynamique depuis les variables d'environnement
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router)
app.include_router(api_keys_router)


@app.get("/")
def read_root():
    return {
        "message": "Profile Service API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else None,
        "graphql": "/graphql"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Docker and Render."""
    return {"status": "healthy", "service": "profile-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)