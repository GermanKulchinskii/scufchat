import strawberry
from fastapi import Depends
from sqlmodel import Session
from strawberry.fastapi import GraphQLRouter

from fapigraphproject import db
from fapigraphproject.graphql_api.mutations import Mutation
from fapigraphproject.graphql_api.queries import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)


def get_context(
    session: Session = Depends(db.get_session),
):
    return {
        "session": session,
    }


graphql_app = GraphQLRouter(schema, context_getter=get_context)
