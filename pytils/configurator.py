def config_var_with_default(var: str, default):
    """Create variable in settings (config) file if it not exist with defined measure.
    If variable already exists on project level, then take the parametr value from file. Value can be changed by user.
    """
    try:
        from config import settings
        if var not in settings:
            from dynaconf.loaders.toml_loader import write
            write('settings.toml', settings_data={var: default}, merge=True)
            return default
        else:
            return settings[var]
    except:
        return default
