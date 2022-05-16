import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from ingredients.schema.category import AddCategoryMutation, CategoryNode, DeleteCategoryMutation, UpdateCategoryMutation
from ingredients.schema.ingredient import AddIngredientMutation, DeleteIngredientMutation, IngredientNode, UpdateIngredientMutation

class Query(graphene.ObjectType):
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

class Mutation(graphene.ObjectType):
    add_ingredient = AddIngredientMutation.Field()
    update_ingredient = UpdateIngredientMutation.Field()
    delete_ingredient = DeleteIngredientMutation.Field()

    add_category = AddCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()
