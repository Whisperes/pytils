def Singleton_args(decorated_class):
    """Decorator for a class to make a singleton out of it.
    Have to be used with @Singleton_args before any class.

    Singleton - a software design pattern that restricts the instantiation of a class to one "single" instance.
    This is useful when exactly one object is needed to coordinate actions across the system.
    """
    class_instances = {}

    def getInstance(*args, **kwargs):
        """ creating or just return the one and only class instance.
            The singleton depends on the parameters used in __init__ """
        key = (decorated_class, args, str(kwargs))
        if key not in class_instances:
            class_instances[key] = decorated_class(*args, **kwargs)
        return class_instances[key]

    return getInstance
