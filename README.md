# pytils
Utils for data python projects. Simple, straightforward, but time saving.

- _pickledays_ - decorator of class. Save the object state to the filesystem after it's initialization for some defined time. Load object after another call.
- _singleton_ - decorator of class. Share object to all calls. There will be only one instance.
- _logger_ - log the info messages to file, stream and discord. 
- _log_ - decorator of function. Log the function call into the logger.
- _configurator_ - additional method for Dynaconf, which create variable in settings file.
- _pandas_table_ - additional method for pandas, which save the DataFrame to specific sheet. Differs from standard df.to_excel by saving other sheets.

# Installation
From the [PiPy](https://pypi.org/project/pytils-functions/):

    pip install pytils-functions

Directly from github:

    pip install git+https://github.com/Whisperes/pytils.git
    
# How to log 
![Discord logs](docs/imgs/pytils.png)
## Straight logs
Log to the handlers: 
* discord webhook, 
* streamhandler 
* timerotation file. 

For each handler you can set your own log level in the settings.toml file in your project (see Dynaconf package)


    from pytils.logger import logger

    logger.debug("this is a debugging message")
    logger.success("this is a success message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.notice("this is a notice message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")
    logger.log(89, "this is a number message")
    
## How to decorate functions for logs
    from pytils.logger import log
    
    @log()
    def my_function(a=[1,3], b=2, c=3):
        //do something

    answer = my_function([11, 'beta'], 2, c=3)

It will be loged like this:

_2022-09-02 18:13:25 my-pc |[3812] DEBUG Processing my_function: ([11, 'beta'], 2), {'c': 3}_

_2022-09-02 18:13:25 my-pc |[3812] SUCCESS my_function: ([11, 'beta'], 2), {'c': 3}_


## Add log level 
Additional levels added to logging module:
* SUCCESS (15)
* NOTICE (25)


    from pytils.logger import addLoggingLevel
    
    addLoggingLevel('MY_LOG_LEVEL', 45)
    
# Cashe
## Cashe object to the disk
    from pytils.pickler import pickledays
    
    @pickledays(period=2)
    class A:
        def __init__(self, var):
            self.var = var
    
    a = A(2)
    
Object A will be saved for 2 days. New call A(2) will take the state of object from pickle file. Req: object have to be immutable.

## No duplicates
    from pytils.singleton import Singleton_args
    
    
    @Singleton_args
    class A:
        def __init__(self, var):
            self.var = var
    
    a = A(2)
Just singleton this. Your object with sspecific set of args will be be the only one through the whole code.

## Retry errors
    @retry(retries=5, delay=1)
    def example_function():
        import random
        if random.random() < 0.8:
            raise ValueError("Random error")
        else:
            return('True')
    
    
    
    example_function()

Decorate function with failing possibility. Delay in seconds.