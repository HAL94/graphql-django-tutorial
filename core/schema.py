import graphene

from ingredients.schema import schema as IngredientSchema

class Query(IngredientSchema.Query, graphene.ObjectType):
    pass

class Mutation(IngredientSchema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)