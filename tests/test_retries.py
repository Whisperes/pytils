from pytils.retry import retry

@retry(retries=5, delay=1)
def example_function():
    import random
    if random.random() < 1:
        raise ValueError("Random error")
    else:
        return('True')


def test_retires():
    example_function()