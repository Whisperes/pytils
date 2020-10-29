from functools import wraps

import logging
import json
import requests
from socket import gethostname

from pytils.configurator import config_var_with_default

def create_logger():
    agent = "LoggerBot"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create formatter
    FORMAT = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")

    #config check
    #TODO: Secret webhook
    discord_channel = config_var_with_default("LOG_WEBHOOK_DISCORD", 'https://discordapp.com/api/webhooks/748465782551216160/66Yn1W-PlVW5_PItHGxHMQ7ZRtkD37poEtIb9JeMlv3ricIgMEuyz17Sp1LtevDc0drl')
    logfile_path = config_var_with_default("LOG_FOLDER",'./Assets/logs/') + 'logs/'
    discord_level = config_var_with_default("LOG_LEVEL_DISCORD", 'ERROR')
    logfile_level = config_var_with_default("LOG_LEVEL_FILE", 'ERROR')
    stream_level = config_var_with_default("LOG_LEVEL_STREAM", 'DEBUG')


    # Create DiscordHandler, FileHandler and StreamHandler
    discord_handler = DiscordHandler(discord_channel, agent)

    stream_handler = logging.StreamHandler()

    import os
    if not os.path.exists(logfile_path):
        os.makedirs(logfile_path)

    logfile_handler = logging.FileHandler(logfile_path+'logs.txt')

    # Set log level to handlers
    discord_handler.setLevel(discord_level)
    logfile_handler.setLevel(logfile_level)
    stream_handler.setLevel(stream_level)

    # Add format to handlers
    discord_handler.setFormatter(FORMAT)
    logfile_handler.setFormatter(FORMAT)

    # Add the handlers to the Logger
    logger.addHandler(discord_handler)
    logger.addHandler(logfile_handler)
    logger.addHandler(stream_handler)

    logger.info('Logger set up')
    return logger

class DiscordHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a Discord Server using webhooks.
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

        request = requests.post(self._url,
                                headers=self._header,
                                data=content, verify=False)

        if request.status_code == 404:
            raise requests.exceptions.InvalidURL(
                "This URL seams wrong... Response = %s" % request.text)

        if request.ok == False:
            raise requests.exceptions.HTTPError(
                "Request not successful... Code = %s, Message = %s" % request.status_code, request.text)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.write_to_discord("```%s```" % msg)
        except Exception:
            self.handleError(record)

def log(level = 'DEBUG'):
    def log_without_level(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if level == 'DEBUG':
                    logger.debug(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'INFO':
                    logger.info(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'WARNING':
                    logger.warning(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                elif level == 'ERROR':
                    logger.error(msg="{0} - {1} - {2}".format(func.__name__, args, kwargs))
                res = func(*args, **kwargs)
            except Exception as ex:
                logger.exception("{0} - {1} - {2} \n {3}".format(func.__name__, args, kwargs, ex))
                raise ex
            return res
        return wrapper
    return log_without_level


create_logger()
logger = logging.getLogger("Application")