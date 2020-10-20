from pytils.pickler import *

@pickledays()
class Ticker():
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)

    @property
    def RIC(self):
        if self.id == 'IMOEX':
            return '.IMOEX'
        else:
            return None


Ticker(1)
