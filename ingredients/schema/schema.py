import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from ingredients.models import Category, Ingredient

from ingredients.schema.category import AddCategoryMutation, CategoryNode, DeleteCategoryMutation, UpdateCategoryMutation
from ingredients.schema.ingredient import AddIngredientMutation, DeleteIngredientMutation, IngredientNode, UpdateIngredientMutation
from core.utils import redis_instance
from graphql_jwt.decorators import login_required

class Query(graphene.ObjectType):    
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)
    
    @login_required
    def resolve_all_categories(root, info, **kwargs):
        return Category.objects.filter(user=info.context.user)
        # cats = redis_instance.get('cats')
        
        # if cats is not None:
        #     return cats
        # else:
        #     cats = Category.objects.filter(user=info.context.user)
        #     redis_instance.set('cats', cats)
        #     return cats

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

    @login_required
    def resolve_all_ingredients(root, info, **kwargs):
        return Ingredient.objects.filter(user=info.context.user)

class Mutation(graphene.ObjectType):
    add_ingredient = AddIngredientMutation.Field()
    update_ingredient = UpdateIngredientMutation.Field()
    delete_ingredient = DeleteIngredientMutation.Field()

    add_category = AddCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()

