from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.graphql import router as graphql_router
from api.api_keys import router as api_keys_router
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Profile Service",
    description="Microservice for managing user profiles",
    lifespan=lifespan
)

app.include_router(graphql_router)
app.include_router(api_keys_router)


@app.get("/")
def read_root():
    return {"message": "Profile Service API", "docs": "/docs", "graphql": "/graphql"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)