from pytils.configurator import *
from functools import wraps

from pytils.logger import logger

import glob
import itertools
import dill
import string
import os

period = config_var_with_default('PICKLE_PERIOD_DEFAULT',1)
def pickledays(period = period):
    def picklecache(func):
        #Важна последовательность
        path_pickle=config_var_with_default('PATH_PICKLE','./Assets/pickle/') + func.__name__

        def makename(*args, **kwargs):
            name = ''
            for sublist in args:
                if isinstance(sublist,dict):
                    for el in sorted(sublist.keys()):
                        name += str(el)[:10]+str(sublist[el])[:20]
                else:
                    for el in sublist:
                        name += str(el)[:20]
            if name == '':
                name = 'NA'
            return path_pickle + '/' +name

        def clearcache(*args, **kwargs):
            '''
            delete the cached result for these particular arguments
            '''
            cachename = makename(args, kwargs)
            try:
                os.remove(cachename)

            except FileNotFoundError:
                pass

        def clearallcache():
            '''
            delete all chached results for this function
            '''
            for f in glob.iglob(''.join(('.*', func.__name__, '_picklecache'))):
                try:
                    os.remove(f)
                except FileNotFoundError:
                    pass

        @wraps(func)
        def wrapper(*args, **kwargs):
            '''
            wrapper which does the actual caching
            '''
            cachename = makename(args, kwargs)

            def write():
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
                if ftime.days > period:
                    logger.info('{} smell during {} > {}. Try to reload.'.format(func.__name__, ftime, period))
                    raise
                else:
                    logger.debug('{} fresh {}'.format(func.__name__, ftime))
                    result = read()
            except:
                result = write()
            return result

        # attach clearcache and clearallcache to wrapper
        wrapper.clearcache = clearcache
        wrapper.clearallcache = clearallcache

        return wrapper
    return picklecache

