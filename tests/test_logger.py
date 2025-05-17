from pytils.logger import *
"""All tests here are not automated."""

@log('WARNING', True)
def func_tst(a=[1,3], b=2, c=3):
    return True

@log('WARNING', True)
def func_with_error(a=[1,3], b=2, c=3):
    raise ValueError('testError')


def test_log():
    answer = func_tst()
    # TODO check the print in StreamHandler and File
    assert answer


def test_log_with_args():
    answer = func_tst([11, 'beta'], 2, c=3)
    # TODO check the print in StreamHandler and File
    assert answer


def test_func_exception():
    try:
        answer = func_with_error([11, 'beta'], 2, c=3)
    except ValueError as ex:
        logger.exception('test accepted', ex)
        assert True

def test__la_exception():
    try:
        ValueError('sdf')
    except ValueError as ex:
        logger.error('test accepted', ex)

def test_colors():
    logger.debug("this is a debugging message")
    logger.success("this is a success message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.notice("this is a notice message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")
    for e in range(20):
        print(f'{e}')
    logger.log(89, "this is a number message")


def test_loggers_conflict():
    logger.critical("this is a critical message")
    create_logger(__name__)
    logger2 = logging.getLogger(__name__)
    logger2.critical("this is a another critical message")


def test_highload():
    for e in range(50):
        logger.error(f'{e}')


def test_root_logger():
    lg = logging.getLogger()
    lg.critical("ROOT message")
    assert True