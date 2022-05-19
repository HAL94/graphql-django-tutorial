import copy
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from ingredients.models import Category, Ingredient

class IngredientNode(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)
    
    class Meta:
        model = Ingredient
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        interfaces = (relay.Node, )
    
    @staticmethod    
    def from_global_id(cls, global_id):
        return global_id

class AddIngredientMutation(graphene.Mutation):
    ingredient = graphene.Field(IngredientNode)

    class Arguments:
        name = graphene.String()
        notes = graphene.String()
        category_id = graphene.Int()
    
    def mutate(self, info, **input):
        ingredient = Ingredient()
        ingredient.name = input['name']
        ingredient.notes = input['notes']
        
        category = Category.objects.get(pk=input['category_id'])
        if category is None:
            return Exception('ID passed is invalid')
        
        ingredient.category = category
        ingredient.save()

        return AddIngredientMutation(ingredient=ingredient)

class UpdateIngredientMutation(graphene.Mutation):
    ingredient = graphene.Field(IngredientNode)

    class Arguments:
        ingredient_id = graphene.Int()
        name = graphene.String()
        notes = graphene.String()
        category_id = graphene.Int()
    
    def mutate(self, info, **input):
        if 'ingredient_id' not in input:
            return Exception('Ingredient ID passed is invalid')
        elif input['ingredient_id'] is None:
            return Exception('Ingredient ID passed is incorrect')
        
        ingredient = Ingredient.objects.filter(pk=input['ingredient_id']).first()        

        if 'category_id' in input:
            category = Category.objects.filter(pk=input['category_id']).first()
            if category is None:
                return Exception('Category ID passed is incorrect')
            else:
                ingredient.category = category
        
        if 'name' in input:
            if input['name'] == '':
                return Exception('Name field is empty!')
            else:
                ingredient.name = input['name']

        if 'notes' in input:
            if input['notes'] == '':
                return Exception('Notes field is empty')
            else:
                ingredient.notes = input['notes']

        ingredient.save()

        return UpdateIngredientMutation(ingredient=ingredient)

class DeleteIngredientMutation(graphene.Mutation):
    ingredient = graphene.Field(IngredientNode)

    class Arguments:
        ingredient_id = graphene.Int()
    
    def mutate(self, info, **input):
        if input['ingredient_id'] is None:
            return Exception('Ingredient ID passed is invalid')
        
        ingredient = Ingredient.objects.filter(pk=input['ingredient_id']).first()

        if ingredient is None:
            return Exception('Ingredient ID passed is incorrect')
        
        mutation = DeleteIngredientMutation(ingredient=copy.copy(ingredient))

        ingredient.delete()

        return mutation
