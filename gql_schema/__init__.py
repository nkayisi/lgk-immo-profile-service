"""
GraphQL Schema package.
"""
import strawberry
from gql_schema.profile_queries import ProfileQuery
from gql_schema.profile_mutations import ProfileMutation
from gql_schema.profile_types import (
    ProfileUnion,
    IndividualProfileType,
    BusinessProfileType,
    ProfileDocumentType,
    ProfileVerificationType,
    ProfileInterface,
)


@strawberry.type
class Query(ProfileQuery):
    """Root Query - hérite de toutes les queries."""
    pass


@strawberry.type
class Mutation(ProfileMutation):
    """Root Mutation - hérite de toutes les mutations."""
    pass


# Schéma GraphQL principal
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    types=[IndividualProfileType, BusinessProfileType],
)

__all__ = ["schema"]
