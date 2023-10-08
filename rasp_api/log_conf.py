# -*- coding: utf-8 -*-
"""
Конфигурация логгера.
"""
import logging
import sys

from os import path
from datetime import datetime

LOG_PATH = f"{path.join(path.dirname(path.abspath(__file__)), '../files/debug.log')}"


class Formatter(logging.Formatter):
    """
    Форматтер логгирования.
    """
    max_level_length = 9
    max_module_length = 14
    max_func_length = 15
    max_line_length = 5
    max_thread_length = 14

    def format(self, record: logging.LogRecord) -> str:
        level, module, func, line, thread = \
            record.levelname, record.module, record.funcName, record.lineno, record.threadName
        message = str(record.msg).replace('\n', ' ')

        time = datetime.now().strftime('%Y-%d-%m / %H:%M:%S')

        if len(level) <= self.max_level_length:
            level = f"{level}" + " " * (self.max_level_length - len(level))

        if len(module) <= self.max_module_length:
            module = f"{module}" + " " * (self.max_module_length - len(module))

        if len(func) + len(record.args) <= self.max_func_length:
            func = f"{func}{record.args}" + " " * (self.max_func_length - len(func))

        if len(str(line)) <= self.max_line_length:
            line = f"{line}" + " " * (self.max_line_length - len(str(line)))

        if len(thread) <= self.max_thread_length:
            thread = f"{thread}" + " " * (self.max_thread_length - len(thread))
        return f"{time} [ {level} ] | {thread} | {module} | Func: {func} | Line: {line} | {message}"


formatter = Formatter()

consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setFormatter(formatter)

filelogHandler = logging.FileHandler(filename=LOG_PATH)
filelogHandler.setFormatter(formatter)

BASIC_FORMAT = "%(asctime)s | [%(levelname)s] | %(module)s Func: %(funcName)s() " \
               "Line: %(lineno)d| %(message)s"

logging.basicConfig(
    level=logging.INFO,
    handlers=[consoleHandler, filelogHandler]
)
