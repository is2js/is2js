import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


def requests_url(url, params=None):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=3)
        response.raise_for_status()  # Raises :class:`HTTPError`, if one occurred.
        return response.text
    except requests.exceptions.ReadTimeout:
        parse_logger.error(f'[ReadTimeout] requests 요청 실패( url: {url})', exc_info=True)
    except requests.HTTPError:
        parse_logger.error(f'[HTTPError] requests 요청 실패( url: {url})', exc_info=True)
    except requests.exceptions.ConnectionError:
        parse_logger.error(f'[ConnectionError] requests 요청 실패( url: {url})', exc_info=True)

    return False


import os
import logging
from logging.handlers import TimedRotatingFileHandler

from rss_sources.config import SourceConfig


class Logger:
    def __init__(self, log_name, backup_count=10):
        self.log_name = log_name

        self.log_dir = SourceConfig.LOG_FOLDER
        self.log_file = os.path.join(self.log_dir, f'{self.log_name}.log')

        self._levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        self._log_format = '%Y-%m-%d %H:%M:%S'

        # 폴더 만들기 -> 여러 경로의 폴더를 이어서 만들 땐, os.makedirs( , exist_ok=True)로 한다
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

        # formatter
        formatter = logging.Formatter(
            '[ %(levelname)s ] %(asctime)s %(filename)s:%(lineno)d %(message)s',
            datefmt=self._log_format
        )

        # handler with formatter
        handler = TimedRotatingFileHandler(
            filename=self.log_file,
            backupCount=backup_count,
            when="midnight",  # 12시마다 잘라서, 10개 반복
        )
        handler.suffix = "%Y%m%d"
        handler.setFormatter(formatter)

        # logger with handler + levels
        self._logger = logging.getLogger(self.log_name)
        self._logger.addHandler(handler)
        self._logger.setLevel(self._levels.get("DEBUG"))

    @property
    def getLogger(self):
        return self._logger


parse_logger = Logger("parse").getLogger
db_logger = Logger("db").getLogger