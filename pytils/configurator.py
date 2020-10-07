def config_var_with_default(var,default):
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
