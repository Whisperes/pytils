def Singleton_args(theClass):
    """Decorator for a class to make a singleton out of it.
    Have to be used with @Singleton_args before any class.

    Singleton - a software design pattern that restricts the instantiation of a class to one "single" instance.
    This is useful when exactly one object is needed to coordinate actions across the system.
    """
    classInstances = {}

    def getInstance(*args, **kwargs):
        """ creating or just return the one and only class instance.
            The singleton depends on the parameters used in __init__ """
        key = (theClass, args, str(kwargs))
        if key not in classInstances:
            classInstances[key] = theClass(*args, **kwargs)
        return classInstances[key]

    return getInstance
