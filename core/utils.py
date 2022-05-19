import graphene
from strenum import StrEnum

MOBILE = 'mobile'
EMAIL = 'email'
AUTH_METHOD_CHOICES = ((MOBILE, 'mobile'), (EMAIL, 'email'))

class AppError(graphene.ObjectType):
    error_title = graphene.String(required=True)
    error_description = graphene.String(required=True)


class AuthMethod(StrEnum):
    MOBILE = 'mobile'
    EMAIL = 'email'