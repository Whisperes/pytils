import json
import logging
from functools import wraps
from socket import gethostname

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pytils.configurator import config_var_with_default

# totally reject the SSL check. Important information have to be logged without this module.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
     addLoggingLevel('TRACE', logging.DEBUG - 5)
     logging.getLogger(__name__).setLevel("TRACE")
     logging.getLogger(__name__).trace('that worked')
     logging.trace('so did this')
     logging.TRACE
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def create_logger():
    # agent = f"{__name__}Bot"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # define list of log handlers. Unified for further usage.
    # unpublic discord server have to be changed in config files.
    discord_channel = config_var_with_default("LOG_WEBHOOK_DISCORD",
                                              'https://discordapp.com/api/webhooks/748465782551216160/66Yn1W-PlVW5_PItHGxHMQ7ZRtkD37poEtIb9JeMlv3ricIgMEuyz17Sp1LtevDc0drl')
    logfile_path = config_var_with_default("LOG_FOLDER", './Assets/logs/') + 'logs/'

    # Define level of allers
    discord_level = config_var_with_default("LOG_LEVEL_DISCORD", 'ERROR')
    logfile_level = config_var_with_default("LOG_LEVEL_FILE", 'ERROR')
    stream_level = config_var_with_default("LOG_LEVEL_STREAM", 'DEBUG')

    # Create DiscordHandlerand StreamHandler
    discord_handler = DiscordHandler(discord_channel)

    stream_handler = logging.StreamHandler()

    # Create FileHandler
    import os
    if not os.path.exists(logfile_path):
        os.makedirs(logfile_path)

    logfile_handler = logging.FileHandler(logfile_path + 'logs.txt')

    # Set log level to handlers
    discord_handler.setLevel(discord_level)
    logfile_handler.setLevel(logfile_level)
    stream_handler.setLevel(stream_level)

    # Create formatter
    logs_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Add format to handlers
    discord_handler.setFormatter(logs_format)
    logfile_handler.setFormatter(logs_format)
    # stream_handler.setFormatter(logs_stream_format)

    # Add the handlers to the Logger
    logger.addHandler(discord_handler)
    logger.addHandler(logfile_handler)
    logger.addHandler(stream_handler)

    # add log levels
    addLoggingLevel('SUCCESS', 15, methodName=None)
    addLoggingLevel('NOTICE', 25, methodName=None)

    # add colors to stram logs
    import coloredlogs
    coloredlogs.install(level='DEBUG',
                        logger=logger,
                        level_styles = {'debug': {'color': 95},
                                        'success': {'color': 46},
                                        'info': {'color': 'blue'},
                                        'notice': {'color': 'magenta'},
                                        'warning': {'color': 'yellow'},'error': {'color': 'red'},
                                        'critical': {'bold': True, 'color': 'red'}})

    logger.info('Logger set up')
    return logger


class DiscordHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted, to a Discord Server using webhooks.
    """

    def __init__(self, webhook_url, agent=None):
        logging.Handler.__init__(self)

        if webhook_url is None or webhook_url == "":
            raise ValueError("webhook_url parameter must be given and can not be empty!")

        if agent is None or agent == "":
            agent = gethostname()

        self._url = webhook_url
        self._agent = agent
        self._header = self.create_header()
        self._name = ""

    def create_header(self):
        return {
            'User-Agent': self._agent,
            "Content-Type": "application/json"
        }

    def write_to_discord(self, message):
        content = json.dumps({"content": message})

        try:
            request = requests.post(self._url,
                                    headers=self._header,
                                    data=content,
                                    verify=False,
                                    timeout=1)
        except requests.exceptions.ReadTimeout as ex:
            logger.debug('Discord logs timed out')
            raise ConnectionError
            # raise requests.exceptions.ReadTimeout

        if request.status_code == 404:
            raise requests.exceptions.InvalidURL(
                "This URL seams wrong... Response = %s" % request.text)

        if request.ok is False:
            raise requests.exceptions.HTTPError(
                "Request not successful... Code = %s, Message = %s" % request.status_code, request.text)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.write_to_discord("```%s```" % msg)
        except Exception:
            self.handleError(record)


def log(level='DEBUG'):
    """Decorator for functions, which will log the function request.
    Have to be used with @log(level='YOUR LEVEL') before any function."""

    def log_without_level(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                if level == 'DEBUG':
                    logger.debug(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'INFO':
                    logger.info(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'WARNING':
                    logger.warning(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'ERROR':
                    logger.error(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                # logger.success("{0} - {1} - {2}".format(func.__name__, args, kwargs))
            except Exception as ex:
                logger.exception("{0} - {1} - {2} \n {3}".format(func.__name__, args, kwargs, ex))
                raise ex
            return res
        return wrapper
    return log_without_level


create_logger()
logger = logging.getLogger("Application")
