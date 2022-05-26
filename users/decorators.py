from functools import wraps

def user_owns(resource, key = None):
    def decorator(func):
        @wraps(func)
        def wrapper(instance, info, *args, **kwargs):
            current_user = info.context.user
            resource_instance = resource.objects.filter(id=kwargs[key]).first()
            if not resource_instance:
                raise Exception(f'Resource not found')
            
            elif not resource._meta.get_field('user'):
                raise Exception(f"Current Resource is not configured to any user")
            
            elif not resource_instance.user == current_user:
                raise Exception(f"{current_user} has no access to this resource")
            
            return func(instance, info, *args, **kwargs)
        return wrapper
    return decorator