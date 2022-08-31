import pytest

from pytils.singleton import Singleton_args


@Singleton_args
class Example:
    """Text class with few operations, which will be used in test cases."""

    def __init__(self, par=0):
        # Default value will be used for cases where args are not necessery
        self.par = par

    def __add__(self, other):
        self.par += other
        return self.par

    def __eq__(self, other):
        if isinstance(other, int):
            return self.par == other
        elif hasattr(self, 'par'):
            return self.par == other.par
        else:
            return False

    def __str__(self):
        return str(self.par)


num_list = [1, 2, 5]


@pytest.mark.parametrize("num", num_list)
def test_singlon_class_with_args(num):
    test_object1 = Example(num)
    assert test_object1 == num

    test_object2 = Example(num)
    assert test_object2 == num
    assert test_object2 == test_object1

    test_object1 += 2
    assert test_object1 == num + 2
    assert test_object2 == num + 2
    assert test_object2 == test_object1


def test_singlon_class_without_args():
    test_object1 = Example()
    assert test_object1 == 0

    test_object2 = Example()
    assert test_object2 == 0
    assert test_object2 == test_object1

    test_object1 += 2
    assert test_object1 == 2
    assert test_object2 == 2
    assert test_object2 == test_object1
