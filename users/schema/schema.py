# users.schema.schema.py
import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token, create_refresh_token, get_refresh_token
from django.contrib.auth import get_user_model
from graphql_jwt.mixins import RefreshMixin
from graphql_jwt.utils import jwt_decode
from graphql_jwt.settings import jwt_settings
from graphql_jwt.refresh_token.models import RefreshToken
from graphql_jwt.exceptions import JSONWebTokenError, JSONWebTokenExpired
from core.utils import AppError, AuthMethod
import time
from users.utils import create_otp_token, OTP_EXP_TIME_MIN, validate_otp_and_token

class UserType(DjangoObjectType):
    id = graphene.ID(source='pk', required=True)
    class Meta:
        model = get_user_model()
        filter_fields = {
            'id': ['exact', 'icontains', 'istartwith'], 
            'mobile': ['exact', 'icontains', 'istartwith'],
            'email': ['exact', 'icontains', 'istartwith']
        }
    
    @staticmethod
    def from_global_id(cls, global_id):
        return global_id

class VerifyOtpMutation(graphene.Mutation ):
    access_token = graphene.String()
    refresh_token = graphene.String()
    user = graphene.Field(UserType)
    errors = graphene.List(AppError)
    success = graphene.Boolean()

    class Arguments:
        otp = graphene.String(required=True)
        register_token = graphene.String(required=True)
    
    def mutate(self, info, **input):
        try:
            otp = input['otp']
            token = input['register_token']
            print(f'received token {token}')
            validate_otp_and_token(token, otp)
            


        except Exception as e:
            print('something went wrong here', e)
            raise ValueError(f'Error: {e}')


class RegisterMutation(graphene.Mutation ):    
    # user = graphene.Field(UserType)
    register_token = graphene.String()
    errors = graphene.List(AppError)
    success = graphene.Boolean()
    otp = graphene.String()
    
    exp_time_seconds = graphene.Int()
    # refresh_token = graphene.String()

    class Arguments:
        auth_method = graphene.Enum.from_enum(AuthMethod)(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)        
    
    def mutate(self, info, **input):
        try:                  
            chosen_method = AuthMethod[input['auth_method'].upper()]
            username = input['username']
            password = input['password']        
            found_user = get_user_model().objects.filter(username=username).first()

            if found_user is not None:                
                return RegisterMutation(success=False,errors=[AppError(error_title="User", error_description="'User Already Exists'")])
            
            user = get_user_model().objects.create_user(auth_method=chosen_method, username=username, password=password)

            # token = get_token(user)            
            otp_token_obj = create_otp_token(user)
            # refresh_token = create_refresh_token(user)

            # return RegisterMutation(user=user, exp_time_seconds = exp_time_min*60, token=token, success=True, errors=None)
            return RegisterMutation(exp_time_seconds = OTP_EXP_TIME_MIN*60, register_token=otp_token_obj['token'], otp=otp_token_obj['otp'], success=True, errors=None)
        except Exception as e:
            print('an error occured', e)
            return RegisterMutation(errors=[AppError(error_title="Unknown Error", error_description=e)])
            

class LoginMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
    errors = graphene.List(AppError)
    success = graphene.Boolean()

    class Arguments:        
        username = graphene.String(required=True)
        password = graphene.String(required=True)
    
    def mutate(self, info, **input):
        try:
            if input['username'] == '' or input['password'] == '':                
                return LoginMutation(token=None, refresh_token=None, user=None, errors=[AppError(error_title="Username Or Password", error_description="Username AND Password must be BOTH passed")])
            
            username = input['username']
            password = input['password']

            # print(f'received props {username} {password}')

            found_user = get_user_model().objects.filter(username=username).first()       
            
            # print(f'found user? {found_user}')

            if found_user is None:                
                return LoginMutation(success=False, errors=[AppError(error_title="User Invalid", error_description="Could not validate the given credentials")])
            
            if not found_user.check_password(password):                
                return LoginMutation(success=False, errors=[AppError(error_title="User Invalid", error_description="Could not validate the given credentials")])

            token = get_token(found_user)
            try:
                RefreshToken.objects.filter(user=found_user).latest("created").delete()
            except RefreshToken.DoesNotExist as dne:
                print(dne)
            
            refresh_token = create_refresh_token(found_user)
            return LoginMutation(user=found_user, token=token, refresh_token=refresh_token)
        
        except Exception as e:
            print('an error occured', e)
            return LoginMutation(errors=[AppError(error_title="Unknown Error", error_description=e)])

class RefreshMutation(RefreshMixin, graphene.Mutation):
    token = graphene.Field(graphene.String)
    refresh_token = graphene.Field(graphene.String)
    errors = graphene.List(AppError)
    refresh_token_expires = graphene.Field(graphene.Int)

    class Arguments(RefreshMixin.Fields):
        pass
         
    @staticmethod
    def mutate(self, info, **input):
        try:                
            context = info.context
            refresh_token = get_refresh_token(input['refresh_token'], context)        

            if refresh_token.is_expired():
                raise JSONWebTokenExpired('Refresh token is expired')
            
            decoded = jwt_settings.JWT_PAYLOAD_HANDLER(refresh_token.user, context)
            user = get_user_model().objects.get(username=decoded['username'])
            rt = RefreshToken.objects.filter(user_id=user.id).latest("created")
            rt.delete()
            token = get_token(user)
            refresh_token = create_refresh_token(user)        
            orig_iat = time.mktime(refresh_token.created.timetuple())            
            print(refresh_token.created, orig_iat, jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds())
            exp = orig_iat + jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()

            return RefreshMutation(token=token, refresh_token=refresh_token, refresh_token_expires=exp, payload=jwt_decode(token))            

        except JSONWebTokenExpired:
            return RefreshMutation(errors=[AppError(error_title="RefreshToken", error_description="Refresh Token Expired")])
        except JSONWebTokenError:
            return RefreshMutation(errors=[AppError(error_title="RefreshToken", error_description="Invalid Refresh Token")])
        
class Mutation(graphene.ObjectType):
    login = LoginMutation.Field()
    register = RegisterMutation.Field()
    refresh_token = RefreshMutation.Field()
    verify_otp = VerifyOtpMutation.Field()
    verify_token = graphql_jwt.Verify.Field()
    revoke_token = graphql_jwt.Revoke.Field()

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure: Your must be signed in')
        return user


schema = graphene.Schema(query=Query, mutation=Mutation)
