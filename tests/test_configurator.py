from pytils.configurator import config_var_with_default


def test_config_var_with_default():
    ans = config_var_with_default('test_var', 'test_value')
    assert ans == 'test_value'
    ans = config_var_with_default('test_var', None)
    assert ans is None