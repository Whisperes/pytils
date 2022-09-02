from pytils.pickler import pickledays

from tests.obj_test import obj


def ak():
    @pickledays(2)
    def obs(*args,**kwargs): return obj(*args,**kwargs)

    s = obs(5)
    print(s.a)
    return ak