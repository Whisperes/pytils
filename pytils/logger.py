import json
import logging
from logging.handlers import TimedRotatingFileHandler
from functools import wraps
from socket import gethostname

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pytils.handler_telegram import TelegramLoggingHandler
from pytils.configurator import config_var_with_default

# totally reject the SSL check. Important information have to be logged without this module.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def addLoggingLevel(levelName: str, levelNum: int, methodName=None):
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

def create_logger(name = __name__,
                  discord_webhook = config_var_with_default("LOG_WEBHOOK_DISCORD",
                                              'https://discordapp.com/api/webhooks/748465782551216160/66Yn1W-PlVW5_PItHGxHMQ7ZRtkD37poEtIb9JeMlv3ricIgMEuyz17Sp1LtevDc0drl'),
                  telegram_token = config_var_with_default("LOG_WEBHOOK_TELEGRAM", "8047232333:AAFEgTeAncBTlJh8wFNvg7dHWaQMZpS4GMM"),
                  telegram_channel = config_var_with_default("LOG_CHANNEL_TELEGRAM", -1001493831691),
                  telegram_thread = config_var_with_default("LOG_THREAD_TELEGRAM", None),

                  ):
    # agent = f"{__name__}Bot"
    logger = logging.getLogger(name)

    # define list of log handlers. Unified for further usage.
    # unpublic discord server have to be changed in config files.
    discord_channel = discord_webhook
    logfile_path = config_var_with_default("LOG_FOLDER", './Assets/logs/')

    # Define level of allers
    discord_level = config_var_with_default("LOG_LEVEL_DISCORD", 101)
    logfile_level = config_var_with_default("LOG_LEVEL_FILE", 'ERROR')
    stream_level = config_var_with_default("LOG_LEVEL_STREAM", 'DEBUG')
    telegram_level = config_var_with_default("LOG_LEVEL_TELEGRAM", 'ERROR')

    # Create DiscordHandlerand StreamHandler
    discord_handler = DiscordHandler(discord_channel)

    telegram_handler = TelegramLoggingHandler(bot_token=telegram_token, channel=telegram_channel, message_thread_id=telegram_thread)

    stream_handler = logging.StreamHandler()

    # Create FileHandler
    import os
    if not os.path.exists(logfile_path):
        os.makedirs(logfile_path)

    logfile_handler = TimedRotatingFileHandler(logfile_path + 'log', when='D', backupCount=14)

    # Set log level to handlers
    discord_handler.setLevel(discord_level)
    logfile_handler.setLevel(logfile_level)
    stream_handler.setLevel(stream_level)
    telegram_handler.setLevel(telegram_level)

    # Create formatter
    logs_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    telegram_format = logging.Formatter("%(levelname)s %(message)s")

    # Add format to handlers
    discord_handler.setFormatter(DiscordFormatter())
    # discord_handler.setFormatter(logs_format)
    logfile_handler.setFormatter(logs_format)
    telegram_handler.setFormatter(telegram_format)
    # stream_handler.setFormatter(logs_stream_format)

    # Add the handlers to the Logger
    logger.addHandler(discord_handler)
    logger.addHandler(logfile_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(telegram_handler)


    # add colors to stram logs
    import coloredlogs
    coloredlogs.install(level='DEBUG',
                        logger=logger,
                        level_styles={'debug': {'color': 95},
                                      'success': {'color': 46},
                                      'info': {'color': 'blue'},
                                      'notice': {'color': 'magenta'},
                                      'warning': {'color': 'yellow'},
                                      'error': {'color': 'red'},
                                      'critical': {'bold': True, 'color': 'red'}})

    logger.debug(f'Logger {name} set up')
    return logger


class DiscordFormatter(logging.Formatter):
    colormap = {'CRITICAL': 0xa11f1f, 'ERROR': 0xd10909,
                'WARNING': 0xb76b0d, 'NOTICE': 0x7c4605,
                'SUCCESS': 0x28a904, 'INFO': 0x0867af,
                'DEBUG': 0x676a6c
                }

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.
        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        Build the discord component https://autocode.com/tools/discord/embed-builder/
        """
        return {"embeds": [
                            {
                              "type": "rich",
                              "description": record.msg,
                              "color": self.colormap[record.levelname] if record.levelname in self.colormap else 0x181c20,
                              "timestamp": self.formatTime(record),
                              "footer": {
                                "text": f"{record.levelname} in {record.module}"
                              }
                            }]}

    def format(self, record) -> str:
        """
        Mostly the same as the parent's class method, the difference being that a dict is manipulated and dumped as JSON
        instead of a string.
        """
        message_dict = self.formatMessage(record)

        # TODO Format exception. Code below, but posts are too big
        # if record.exc_info:
        #     # Cache the traceback text to avoid converting it multiple times
        #     # (it's constant anyway)
        #     if not record.exc_text:
        #         message_dict["embeds"][0].update({"title": record.message,
        #                                           'description': self.formatException(record.exc_info)})
        return json.dumps(message_dict, default=str)



class DiscordHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted, to a Discord Server using webhooks.
    Thx https://github.com/TrayserCassa/DiscordHandler
    """

    def __init__(self, webhook_url: str, agent=None):
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

    def write_to_discord(self, message: str):
        try:
            #TODO use async thread for not waiting the answer from Discord
            request = requests.post(self._url,
                                    headers=self._header,
                                    data=message,
                                    verify=False,
                                    timeout=1)
        except requests.exceptions.ReadTimeout as ex:
            pass
            # logger.debug('Discord logs timed out')
            # raise ConnectionError('Discord timeout')
            # raise requests.exceptions.ReadTimeout
        except:
            pass

        if request.status_code == 404:
            pass
            # raise requests.exceptions.InvalidURL(
            #     "This URL seams wrong... Response = %s" % request.text)

        if request.ok is False:
            pass
            # raise requests.exceptions.HTTPError(
            #     "Request not successful... Code = %s, Message = %s" % request.status_code, request.text)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.write_to_discord(msg)
        except Exception:
            self.handleError(record)


def log(level=None, arg_included=True):
    """Decorator for functions, which will log the function request.
    Have to be used with @log(level='YOUR LEVEL') before any function.
    """

    def log_without_level(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if arg_included:
                    msg = "{0}: {1}, {2}".format(func.__name__, str(args), str(kwargs))
                else:
                    msg = func.__name__
                logger.debug(f"Processing {msg}", extra={'argi': args, 'kwargi': kwargs})
                res = func(*args, **kwargs)
                if level is None:
                    logger.success(msg)
                elif level == 'DEBUG':
                    logger.debug(msg)
                elif level == 'INFO':
                    logger.info(msg)
                elif level == 'WARNING':
                    logger.warning(msg)
                elif level == 'ERROR':
                    logger.error(msg)
                elif isinstance(level, int):
                    logger.log(msg, level=level)
                else:
                    raise AttributeError('Error for @log decorator arguments')
            except Exception as ex:
                logger.exception("{0}: {1}, {2} \n {3}".format(func.__name__, str(args), str(kwargs), ex))
                raise ex
            return res

        return wrapper

    return log_without_level


# add log levels into logging module
addLoggingLevel('SUCCESS', 15, methodName=None)
addLoggingLevel('NOTICE', 25, methodName=None)


#create one logger for reserve goals. Just import module with "from pytils.logger import logger" and use in your programm
create_logger("|")
logger = logging.getLogger("|")
