from fastapi import APIRouter, Depends, Request
from strawberry.fastapi import GraphQLRouter
from gql_schema import schema
from core.database import get_db
from core.security import verify_api_key
from sqlalchemy.ext.asyncio import AsyncSession


async def get_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    api_key = Depends(verify_api_key)
):
    return {
        "request": request,
        "db": db,
        "api_key": api_key
    }


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context
)

router = APIRouter()
router.include_router(graphql_router, prefix="/graphql", tags=["graphql"])