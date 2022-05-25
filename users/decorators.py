from graphql_jwt.decorators import user_passes_test

def verify_jwt(token):
    """ NOT BEING USED CURRENTLY """
    pass
    # print('received token @ decorator', token, type(token), token.is_authenticated)

valid_jwt_required = user_passes_test(verify_jwt)