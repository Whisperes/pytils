
from pytils.pickler import *

@picklecache
class sumss():
    def __init__(self, a, b):
        self.a = a*16

@picklecache
class des():
    def __init__(self):
        import datetime
        self.a = datetime.datetime.now()

# @picklecache
def ss(s):
    return sumss(s)

k = des()
# import pickle
# pickle.dump(k, open('./Assets/pickle/5', 'wb'))

print(k.a)