# users.schema.schema.py
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token, create_refresh_token, get_user_by_token
from django.contrib.auth import get_user_model
from graphql_jwt.mixins import RefreshMixin
from graphql_jwt.utils import jwt_decode

from users.models import CustomUser
from core.utils import AppError, AuthMethod

# from graphql_auth import mutations
import graphql_jwt

class UserType(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)
    class Meta:
        model = CustomUser
        filter_fields = {
            'id': ['exact', 'icontains', 'istartwith'], 
            'mobile': ['exact', 'icontains', 'istartwith'],
            'email': ['exact', 'icontains', 'istartwith']
        }
    
    @staticmethod
    def from_global_id(cls, global_id):
        return global_id


# graphql_jwt.JSONWebTokenMutation, 
class RegisterMutation(graphene.Mutation ):    
    user = graphene.Field(UserType)
    token = graphene.String()
    errors = graphene.List(AppError)
    success = graphene.Boolean()

    refresh_token = graphene.String()

    class Arguments:
        auth_method = graphene.Enum.from_enum(AuthMethod)(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)        
    
    def mutate(self, info, **input):
        errors = []        
        chosen_method = AuthMethod[input['auth_method'].upper()]
        username = input['username']
        password = input['password']        
        found_user = CustomUser.objects.filter(username=username).first()

        if found_user is not None:
            errors.append(AppError(error_title="User", error_description="'User Already Exists'"))
            return RegisterMutation(success=False,errors=errors)
        
        user = get_user_model().objects.create_user(auth_method=chosen_method, username=username, password=password)        

        token = get_token(user)
        refresh_token = create_refresh_token(user)

        return RegisterMutation(user=user, token=token, refresh_token=refresh_token, success=True, errors=None)

class LoginMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
    errors = graphene.List(AppError)

    class Arguments:        
        username = graphene.String(required=True)
        password = graphene.String(required=True)
    
    def mutate(self, info, **input):
        errors = []

        if input['username'] == '' or input['password'] == '':
            errors.append(AppError(error_title="Username Or Password", error_description="Username AND Password must be BOTH passed"))
            return LoginMutation(token=None, refresh_token=None, user=None, errors=errors)
        
        username = input['username']
        password = input['password']               

        found_user = CustomUser.objects.filter(username=username).first()       
        
        if found_user is None:
            errors.append(AppError(error_title="User Invalid", error_description="Could not validate the given credentials"))
            return LoginMutation(token=None, refresh_token=None, user=None, errors=errors)
        
        if not found_user.check_password(password):
            errors.append(AppError(error_title="User Invalid", error_description="Could not validate the given credentials"))
            return LoginMutation(token=None, refresh_token=None, user=None, errors=errors)
        
        token = get_token(found_user)
        refresh_token = create_refresh_token(found_user)
        return LoginMutation(user=found_user, token=token, refresh_token=refresh_token)

class RefreshMutation(RefreshMixin, graphene.Mutation):
    token = graphene.Field(graphene.String)
    refresh_token = graphene.Field(graphene.String)

    class Arguments(RefreshMixin.Fields):
        """ """
    # from graphql_jwt.refresh_token.models import RefreshToken
    def mutate(self, info, **input):
        print('received refresh_token', input)
        payload = get_user_by_token(input['token'])
        print('is this the user?', payload)
        # print('decoded', jwt_decode(input['token']))
        
        token = get_token(payload)
        refresh_token = create_refresh_token(payload)
        return RefreshMutation(token=token, refresh_token=refresh_token)
    
        

class Mutation(graphene.ObjectType):
    login = LoginMutation.Field()
    register = RegisterMutation.Field()
    verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()
    refresh_token = RefreshMutation.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure: Your must be signed in')
        return user




schema = graphene.Schema(query=Query, mutation=Mutation)
