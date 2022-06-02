import graphene
from strenum import StrEnum
import redis
import json

MOBILE = 'mobile'
EMAIL = 'email'
AUTH_METHOD_CHOICES = ((MOBILE, 'mobile'), (EMAIL, 'email'))

class AppError(graphene.ObjectType):
    error_title = graphene.String(required=True)
    error_description = graphene.String(required=True)


class AuthMethod(StrEnum):
    MOBILE = 'mobile'
    EMAIL = 'email'

# Connect to our Redis instance
redis_instance = redis.StrictRedis()


class Redis:
    def set(cache_key, data):
        data = json.dumps(data)
        redis_instance.set(cache_key, data)

    def get(cache_key):
        return redis_instance.get(cache_key)
