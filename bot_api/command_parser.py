# -*- coding: utf-8 -*-
"""
Модуль обработки комманд
"""
import string

from typing import Union

from pyparsing import Word, Optional


LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" + string.ascii_lowercase
LETTERS_UPPERCASE = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" + string.ascii_uppercase
NUMBERS = "0123456789"


class Command:
    """
    Класс парсинга команды из строки
    """
    def __init__(self, string_: str, prefixes: Union[str, None] = None):
        """
        :param str string_: строка для парсинга
        :param str prefixes: префиксы команды. По умолчанию !#
        """
        if prefixes:
            self.__prefix = Word(prefixes)
        else:
            self.__prefix = Word("!#")

        self.__string = string_
        self.__key = Word(LETTERS)
        self.__argument = Optional(Word(LETTERS + NUMBERS + "-" + LETTERS_UPPERCASE))
        self.__command = self.__prefix + self.__key + self.__argument

        self.command = self.__get_command()
        self.args = self.__get_args()

    def is_command(self) -> bool:
        """
        Является ли команда корректной или нет
        :return: True/False
        """
        try:
            if self.__command.parseString(self.__string):
                return True
        except:
            return False

        return False

    def __get_args(self) -> Union[list, None]:
        if self.is_command() and len(self.__command_list()) > 2:
            return self.__command_list()[2::]
        return None

    def __command_list(self) -> list:
        try:
            return self.__command.parseString(self.__string)
        except:
            return []

    def __get_command(self) -> Union[str, None]:
        if self.is_command():
            return self.__command_list()[1]
        return None
