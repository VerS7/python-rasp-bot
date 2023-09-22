from pyparsing import Word, Optional
from typing import Union

LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
LETTERS_UPCASE = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
NUMBERS = "0123456789"


class Command:
    def __init__(self, string: str, prefixes: Union[str, None] = None):
        """
        Парсинг команды из строки
        :param str string: строка для парсинга
        :param str prefixes: префиксы команды. По умолчанию !#
        """
        if prefixes:
            self.__prefix = Word(prefixes)
        else:
            self.__prefix = Word("!#")

        self.__string = string
        self.__key = Word(LETTERS)
        self.__argument = Optional(Word(LETTERS + NUMBERS + "-" + LETTERS_UPCASE))
        self.__command = self.__prefix + self.__key + self.__argument

        self.command = self.__get_command()
        self.args = self.__get_args()

    def isCommand(self) -> bool:
        """
        Является ли команда корректной или нет
        :return: True/False
        """
        try:
            if self.__command.parseString(self.__string):
                return True
        except:
            return False

    def __get_args(self) -> Union[list, None]:
        if self.isCommand() and len(self.__command_list()) > 2:
            return self.__command_list()[2::]
        else:
            return None

    def __command_list(self) -> list:
        try:
            return self.__command.parseString(self.__string)
        except:
            return []

    def __get_command(self) -> Union[str, None]:
        if self.isCommand():
            return self.__command_list()[1]
        else:
            return None
