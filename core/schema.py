import graphene

from ingredients.schema import schema as IngredientSchema
# from graphql_auth.schema import UserQuery, MeQuery
import users.schema.schema as UserSchema

class Query(IngredientSchema.Query, UserSchema.Query, graphene.ObjectType):
    pass

class Mutation(IngredientSchema.Mutation, UserSchema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)