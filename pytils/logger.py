import logging
from logging.handlers import TimedRotatingFileHandler
from functools import wraps

import requests
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pytils.configurator import config_var_with_default

# totally reject the SSL check. Important information have to be logged without this module.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)

appname = os.environ.get("SERVICE_NAME", config_var_with_default("SERVICE_NAMESPACE","pyapp"))

def add_logging_level(levelName: str, levelNum: int, methodName=None):
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


def create_logger(name=__name__, logger=None,
                  discord_webhook=config_var_with_default("LOG_WEBHOOK_DISCORD",
                                                          'https://discord.com/api/webhooks/1373280677541318786/LeOG3e5mLWekGo4Two30R9iQ_jWX5OKNWfNtlw8ALI_hl383wdPYPPzU0ZNp5kPzEWkV'),
                  telegram_token=config_var_with_default("LOG_WEBHOOK_TELEGRAM",
                                                         "8047232333:AAFEgTeAncBTlJh8wFNvg7dHWaQMZpS4GMM"),
                  telegram_channel=config_var_with_default("LOG_CHANNEL_TELEGRAM", -1001493831691),
                  telegram_thread=config_var_with_default("LOG_THREAD_TELEGRAM", None),
                  # otlp_endpoint: str = config_var_with_default("LOG_THREAD_OTLP", "http://192.168.77.2:4318/v1/logs"),
                  otlp_endpoint: str = config_var_with_default("LOG_THREAD_OTLP", "http://localhost:4318/v1/logs"),
                  ):
    if logger is None:
        logger = logging.getLogger(name)
        logger.propagate = False

    logs_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create FileHandler
    logfile_level = config_var_with_default("LOG_LEVEL_FILE", 'ERROR')
    if logfile_level is not None:
        logfile_path = config_var_with_default("LOG_FOLDER", './Assets/logs/')
        import os
        if not os.path.exists(logfile_path):
            os.makedirs(logfile_path)
        logfile_handler = TimedRotatingFileHandler(logfile_path + 'log', when='D', backupCount=14)
        logfile_handler.setLevel(logfile_level)
        logfile_handler.setFormatter(logs_format)

        logger.addHandler(logfile_handler)

    # Create DiscordHandlerand StreamHandler
    discord_channel = discord_webhook
    discord_level = config_var_with_default("LOG_LEVEL_DISCORD", None)
    if discord_level is not None:
        from pytils.handler_discord import DiscordHandler, DiscordFormatter

        discord_handler = DiscordHandler(discord_channel)
        discord_handler.setLevel(discord_level)
        discord_handler.setFormatter(DiscordFormatter())

        logger.addHandler(discord_handler)

    # Create TelegramHandler
    telegram_level = config_var_with_default("LOG_LEVEL_TELEGRAM", None)
    if telegram_level is not None:
        from pytils.handler_telegram import TelegramLoggingHandler
        telegram_handler = TelegramLoggingHandler(bot_token=telegram_token, channel=telegram_channel,
                                                  message_thread_id=telegram_thread)
        telegram_handler.setLevel(telegram_level)
        telegram_format = logging.Formatter("%(levelname)s %(message)s")
        telegram_handler.setFormatter(telegram_format)

        logger.addHandler(telegram_handler)

    # otlp
    otlp_level = config_var_with_default("LOG_LEVEL_OTLP", 'ERROR')
    if otlp_level is not None:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        # from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

        resource_attrs = {"deployment.environment": os.environ.get("APP_ENV", "dev"),
                           "service.name": appname,
                           "service.namespace": os.environ.get("SERVICE_NAMESPACE",
                                                               config_var_with_default("SERVICE_NAMESPACE","pyapp")),
                        }
        if "CONTAINER_NAME" in os.environ:
            resource_attrs["container.name"] = os.environ.get("CONTAINER_NAME")
        else:
            import socket
            resource_attrs["container.name"] = socket.gethostname()

        resource = Resource(attributes=resource_attrs)

        provider = LoggerProvider(resource=resource)
        exporter = OTLPLogExporter(endpoint=otlp_endpoint)  # insecure=insecure
        processor = BatchLogRecordProcessor(exporter)
        provider.add_log_record_processor(processor)
        otlp_handler = LoggingHandler(level=otlp_level,
                                      logger_provider=provider)

        logger.addHandler(otlp_handler)

    # Stdout
    stream_level = config_var_with_default("LOG_LEVEL_STREAM", 'DEBUG')
    if stream_level is not None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(stream_level)

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

        logger.addHandler(stream_handler)

    logger.debug(f'Logger {name} set up')
    return logger


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
                    logger.log(msg=msg, level=level)
                else:
                    raise AttributeError('Error for @log decorator arguments')
            except Exception as ex:
                logger.exception("{0}: {1}, {2} \n {3}".format(func.__name__, str(args), str(kwargs), ex))
                raise ex
            return res

        return wrapper

    return log_without_level


# add log levels into logging module
add_logging_level('SUCCESS', 15, methodName=None)
add_logging_level('NOTICE', 25, methodName=None)

# create one logger for reserve goals. Just import module with "from pytils.logger import logger" and use in your programm
create_logger(appname)
logger = logging.getLogger(appname)
# root_logger = create_logger(logger=logging.getLogger())

