from graphql_jwt.utils import jwt_decode
from django.contrib.auth import get_user_model
# from graphql_jwt import settings as jwt_settings
# import jwt

""" A sample class detailing how to write your own middleware """
class AuthorizationGraphQLMiddleware:
    """Middleware add User object for each GraphQL resolver info.context"""
    def resolve(self, next, root, info, **kwargs):
        decoded = None
        token = None
        # print('resolver running..')
        auth_header = info.context.META.get('HTTP_AUTHORIZATION')
        # print('middleware auth token here', token)
        if auth_header:
            token = auth_header.split(" ")[1].strip()
            # print(jwt_settings.DEFAULTS)
            # decoded = jwt.decode(jwt=token, key=jwt_settings.DEFAULTS['JWT_SECRET_KEY'], verify=jwt_settings.DEFAULTS['JWT_VERIFY'], options={'verify_exp': True}, audience=None, algorithms=[jwt_settings.DEFAULTS['JWT_ALGORITHM']])
            decoded = jwt_decode(token)
            print('decoded jwt', decoded)

            if decoded is not None:
                # print('decoded token', decoded)
                info.context.user = get_user_model().objects.get(username=decoded['username'])
       

        return next(root, info, **kwargs)