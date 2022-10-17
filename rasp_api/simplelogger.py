# -*- coding: utf-8 -*-
import logging
from datetime import date
from time import strftime, gmtime


"""Простейшая система логгирования исключений"""
logging.basicConfig(filename='error.log', filemode='a')

def loggit(func):
    def wrapped():
        try:
            func()
            print(f"{date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} | {func.__name__} успешно отработала.")
        except Exception as e:
            print(f"{date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} | [{e.__class__}] | {func.__name__} вызвана с ошибкой - {e}.")
            logging.error(msg=f" | {date.today().strftime('%Y-%d-%m')} - {strftime('%H:%M:%S', gmtime())} [{e.__class__}] - {e}")
    return wrapped()