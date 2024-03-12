''' Retry decorator for classes and functions. It retries function execution if the execution was failed by error.

Examples:
    @retry(retries=3):
    def example_func(*args, **kwargs):
        return **kwargs

'''

import functools
import time

from pytils.configurator import config_var_with_default
from pytils.logger import logger


def retry(retries=config_var_with_default('retry_tries',3),
          delay=config_var_with_default('retry_delay',0)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempts + 1}/{retries} failed for {func.__name__}")
                    attempts += 1
                    last_exception = e
                    if delay > 0:
                        time.sleep(delay)

            if last_exception is not None:
                logger.error(f"Function {func.__name__} failed after {retries} attempts")
                raise last_exception
        return wrapper
    return decorator

