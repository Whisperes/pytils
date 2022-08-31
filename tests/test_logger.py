from pytils.logger import *
"""All tests here are not automated."""

@log('ERROR')
def func_tst(a=1, b=2, c=3):
    return True


def test_log():
    answer = func_tst()
    # TODO check the print in StreamHandler and File
    assert answer


def test_log_with_args():
    answer = func_tst(1, 2, c=3)
    # TODO check the print in StreamHandler and File
    assert answer

def test_colors():
    logger.debug("this is a debugging message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")