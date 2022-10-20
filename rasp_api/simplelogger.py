# -*- coding: utf-8 -*-
import logging
from functools import wraps
from datetime import date
from time import strftime, gmtime


"""Простейшая система логгирования исключений"""
logging.basicConfig(filename='error.log', filemode='a')


def loggit(func):
    """Логгирует в консоль и errors.log файл дату, время и ошибку."""
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
            print(f"{date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} | {func.__name__} успешно отработала.")
        except Exception as e:
            print(f"{date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} | [{e.__class__}] | {func.__name__} вызвана с ошибкой - {e}.")
            logging.error(msg=f" | {date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} [{e.__class__}] - {e}")
    return wrapped


def loopexcepter(func):
    """Циклический перевызов функции при её отвале."""
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        while True:
            try:
                func(self, *args, **kwargs)
            except:
                func(self, *args, **kwargs)
    return wrapped
