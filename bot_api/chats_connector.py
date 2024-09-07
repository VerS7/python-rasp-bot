"""
Модуль работы системы подключенных чатов
"""
import json
from os import path
from typing import Union


CHATS_PATH = path.join(path.dirname(path.dirname(path.abspath(__file__))), "files/chats.json")


class Chats:
    """
    Класс системы чатов
    """
    def __init__(self, file_path: str = CHATS_PATH):
        self.__path = file_path
        self.__chats: dict = self.__load_json()

    def get_chats(self) -> dict:
        """
        Возвращает чаты с подключенными группами.
        """
        return self.__chats

    def add_group(self, chat_id: str, groupname: str):
        """
        Сохраняет значение чат: группа
        :param str chat_id: айди чата
        :param str groupname: имя группы
        """
        if not isinstance(chat_id, str):
            chat_id = str(chat_id)

        if chat_id in self.__chats.keys():
            return

        self.__load_json()
        self.__chats[chat_id] = groupname
        self.__dump_json()

    def get_group(self, chat_id: str) -> Union[str, None]:
        """
        Возвращает подключенную группу к chat_id или None
        :param str chat_id: id чата
        :return: имя группы или None
        """
        if not isinstance(chat_id, str):
            chat_id = str(chat_id)

        self.__load_json()

        return self.__chats.get(chat_id, None)

    def in_chats(self, chat_id: str) -> bool:
        """
        :param str chat_id: id чата
        :return: True/False наличие чата в ситсеме оповещений
        """
        if not isinstance(chat_id, str):
            chat_id = str(chat_id)

        if chat_id in self.__chats.keys():
            return True

        return False

    def remove_chat(self, chat_id: str) -> Union[str, None]:
        """
        Удаляет конкретный чат из сохранённых чатов
        :param str chat_id: id чата
        :return: удалённая группа или None в случае отсутствия
        """
        if not isinstance(chat_id, str):
            raise TypeError

        group = self.__chats.pop(chat_id, None)

        if group is not None:
            self.__dump_json()

        return group

    def __load_json(self):
        with open(self.__path, "r", encoding="utf-8") as file:
            return json.load(file)

    def __dump_json(self):
        with open(self.__path, "w", encoding="utf-8") as file:
            return json.dump(self.__chats, file)
