import logging
from socket import gethostname
import json
import requests


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
