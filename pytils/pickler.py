import glob
import os
import dill
import datetime
from functools import wraps
from pytils.configurator import *
from pytils.logger import logger

# How long the object will be fresh? None - option for no usage of pickle. Can be change in config.
period = config_var_with_default('PICKLE_PERIOD_DEFAULT', 1)


def pickledays(period=period):
    def picklecache(func):
        # Path of storage the pickle files.
        path_pickle = config_var_with_default('PATH_PICKLE', './Assets/pickle/') + func.__name__

        def makename(*args, **kwargs):
            """naming the pickle file"""

            # define the function for stringify the arguments
            def convert_type(x):
                if isinstance(x, datetime.datetime):
                    return str(x.date())
                else:
                    # not so long names should be used
                    return str(x)[:20]

            name = ''
            # list through arguments and add them to file name
            for sublist in args:
                if isinstance(sublist, dict):
                    for key in sorted(sublist.keys()):
                        name += convert_type(key) + convert_type(sublist[key])
                else:
                    for key in sublist:
                        name += convert_type(key)
            if name == '':
                name = 'NA'
            return path_pickle + '/' + name

        def clearcache(*args, **kwargs):
            """ delete the cached result for these particular arguments """
            cachename = makename(args, kwargs)
            try:
                os.remove(cachename)

            except FileNotFoundError:
                pass

        def clearallcache():
            """ delete all chached results for this function """

            for f in glob.iglob(''.join(('.*', func.__name__, '_picklecache'))):
                try:
                    os.remove(f)
                except FileNotFoundError:
                    pass

        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper which does the actual caching"""

            cachename = makename(args, kwargs)

            def write():
                # TODO pickle with import issues https://stackoverflow.com/questions/1412787/picklingerror-cant-pickle-class-decimal-decimal-its-not-the-same-object
                if not os.path.exists(path_pickle):
                    os.makedirs(path_pickle)

                result = func(*args, **kwargs)
                dill.dump(result, open(cachename, 'wb'))
                return result

            def read():
                with open(cachename, "rb") as f:
                    result = dill.load(f)
                return result

            try:
                import datetime
                ftime = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cachename)))
                if ftime.days > period or period is None:
                    logger.info('{} smell during {} > {}. Try to reload.'.format(func.__name__, ftime, period))
                    raise FileExistsError
                else:
                    logger.debug('{} fresh {}'.format(func.__name__, ftime))
                    result = read()
            except:
                # if file not founded and read unsuccessful
                result = write()
                logger.debug('{} refreshed'.format(func.__name__))
            return result

        # attach clearcache and clearallcache to wrapper
        wrapper.clearcache = clearcache
        wrapper.clearallcache = clearallcache

        return wrapper

    return picklecache
