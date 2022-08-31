from pytils.logger import *

@log('ERROR')
def func_tst(a = 1, b = 2, c =3):
    return True

def test_log():
    answer = func_tst()
    #TODO check the print in StreamHandler and File
    assert True


def test_log_with_args():
    answer = func_tst(1,2, c = 3)
    #TODO check the print in StreamHandler and File
    assert True
