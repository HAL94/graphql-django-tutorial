import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from ingredients.schema.category import AddCategoryMutation, CategoryNode, DeleteCategoryMutation, UpdateCategoryMutation
from ingredients.schema.ingredient import AddIngredientMutation, DeleteIngredientMutation, IngredientNode, UpdateIngredientMutation

from graphql_jwt.decorators import login_required

class Query(graphene.ObjectType):    
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    @login_required
    def resolve_all_categories(self, info, **kwargs):
        print('resolving context user', info.context.user, kwargs)
        if (info.context.user is not None):
            return 
        return info.context.user

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

class Mutation(graphene.ObjectType):
    add_ingredient = AddIngredientMutation.Field()
    update_ingredient = UpdateIngredientMutation.Field()
    delete_ingredient = DeleteIngredientMutation.Field()

    add_category = AddCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()

