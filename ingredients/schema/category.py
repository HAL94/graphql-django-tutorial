import copy
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from ingredients.models import Category
from graphql_jwt.decorators import login_required

from users.decorators import user_owns


class CategoryNode(DjangoObjectType):    
    id = graphene.ID(source='pk', required=True)

    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        interfaces = (relay.Node, )
        
    @staticmethod
    def from_global_id(cls, global_id):
        return global_id


class AddCategoryMutation(graphene.Mutation):
    category = graphene.Field(CategoryNode)
    
    class Arguments:
        name = graphene.String()    
    
    @login_required
    def mutate(self, info, **input):
        category = Category()
        
        if (input['name'] is None or input['name'] == ''):
            return Exception('Name provided is invalid')
        
        category.name = input['name']
        category.user = info.context.user
        category.save()
        return AddCategoryMutation(category=category)

class UpdateCategoryMutation(graphene.Mutation):
    category = graphene.Field(CategoryNode)
    id = graphene.ID(source='pk', required=True)

    class Arguments:
        category_id = graphene.Int()
        name = graphene.String()
    
    @staticmethod
    def from_global_id(cls, global_id):
        return global_id
    
    @login_required
    @user_owns(Category, 'category_id')
    def mutate(self, info, **input):
        if input['category_id'] is None:
            return Exception('Category ID passed is invalid')
        
        category = Category.objects.filter(pk=input['category_id']).first()

        if category is None:
            return Exception('Category ID passed is incorrect')
        
        category.name = input['name'] if input['name'] else category.name

        category.save()

        return UpdateCategoryMutation(category=category)

class DeleteCategoryMutation(graphene.Mutation):
    category = graphene.Field(CategoryNode)
    
    class Arguments:
        category_id = graphene.Int()
    
    @login_required
    @user_owns(Category, 'category_id')
    def mutate(self, info, **input):
        id = input['category_id']
        if id is None:
            return Exception('Category ID passed is invalid')
        
        print(f'passed id: {id}')

        category = Category.objects.filter(pk=id).first()
        if category is None:
            return Exception('Category ID passed is incorrect')

        mutation = DeleteCategoryMutation(category=copy.copy(category))

        category.delete()

        return mutation



