from typing import Union, Optional
import logging
from time import sleep
import requests
from threading import Thread, Event
from pytils.configurator import config_var_with_default

class MessageBuffer:

    def __init__(self, max_size: int = None):
        self._buffer = ''
        self._max_size = max_size

    def write(self, message: str):
        self._buffer = ''.join([self._buffer, message])[:self._max_size]

    def read(self, count: int):
        result = ''
        result, self._buffer = self._buffer[:count], self._buffer[count:]
        return result

FLUSH_INTERVAL = 5
API_HOST = 'api.telegram.org'
MAX_MESSAGE_SIZE = 4000
MAX_BUFFER_SIZE = 10**16

class TelegramLoggingHandler(logging.Handler):

    def __init__(self,
                 bot_token: str,
                 channel: Union[str, int],
                 message_thread_id: Optional[int] = None,  # Type declared here
                 level=logging.NOTSET):
        super().__init__(level)
        self._url = self._format_url(bot_token, channel, message_thread_id)
        self._buffer = MessageBuffer(MAX_BUFFER_SIZE)
        self._stop_event = Event()  # Event for stopping the thread
        self._writer_thread = None
        self._start_writer_thread()

    @staticmethod
    def _format_url(bot_token: str, channel: Union[str, int], message_thread_id: Optional[int] = None):
        formatted_channel = str(channel)
        if message_thread_id is not None:
            return f'https://{API_HOST}/bot{bot_token}/sendMessage?chat_id={formatted_channel}&message_thread_id={message_thread_id}'
        return f'https://{API_HOST}/bot{bot_token}/sendMessage?chat_id={formatted_channel}'

    def write(self, message):
        try:
            response = requests.post(self._url, data={'text': message}, timeout=5)  # Increased timeout
        except Exception as e:
            pass

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self._buffer.write(f'{message}\n')

    def close(self):
        # Signal the thread to stop
        self._stop_event.set()
        # Wait for the thread to finish
        self._writer_thread.join()

    def _write_manager(self):
        while not self._stop_event.is_set():
            sleep(FLUSH_INTERVAL)
            message = self._buffer.read(MAX_MESSAGE_SIZE)
            if message:
                self.write(message)

    def _start_writer_thread(self):
        self._writer_thread = Thread(target=self._write_manager)
        self._writer_thread.daemon = True
        self._writer_thread.start()
