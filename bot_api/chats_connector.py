"""
Модуль работы системы подключенных чатов
"""

import json
from os import path
from typing import Dict
from abc import ABC, abstractmethod

CHATS_PATH = path.join(
    path.dirname(path.dirname(path.abspath(__file__))), "files/chats.json"
)


class Connector(ABC):
    @abstractmethod
    def get_all(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get(self, chat_id: str) -> str | None:
        pass

    @abstractmethod
    def find(self, groupname: str) -> str | None:
        pass

    @abstractmethod
    def add(self, chat_id: str, groupname: str) -> None:
        pass

    @abstractmethod
    def remove(self, chat_id: str) -> str | None:
        pass


class JsonChatsConnector(Connector):
    """
    Класс системы чатов.
    Чаты хранятся в json-файле
    """

    def __init__(self) -> None:
        self._fp: str = CHATS_PATH
        self._chats: Dict[str, str] = self._load()

    def get_all(self) -> Dict[str, str]:
        """Возвращает все чаты с подключенными группами"""
        return self._chats

    def get(self, chat_id: str) -> str | None:
        """
        Возвращает группу по номеру чата
        :param str chat_id: номер чата
        """
        return self._chats.get(chat_id, None)

    def find(self, groupname: str) -> str | None:
        """
        Возвращает чат по названию группы
        :param str groupname: номер чата
        """
        for k, v in self._chats.items():
            if v == groupname:
                return k

    def add(
        self, chat_id: str, groupname: str, autoload: bool = True, autodump: bool = True
    ) -> None:
        """
        Добавляет чат и группу в чаты
        :param str chat_id: номер чата
        :param str groupname: название группы
        """
        if autoload:
            self._load()

        self._chats[chat_id] = groupname

        if autodump:
            self._dump()

    def remove(
        self, chat_id: str, autoload: bool = True, autodump: bool = True
    ) -> str | None:
        """
        Удаляет группу и чат в систему
        :param str chat_id: номер чата
        :param bool autodump: записать в файл автоматически
        :param bool autoload: загрузить из файла автоматически
        """
        if autoload:
            self._load()

        group = self._chats.pop(chat_id, None)

        if not group:
            return

        if autodump:
            self._dump()

    def check(self, chat_id: str) -> bool:
        """
        Проверяет есть ли чат в системе
        :param chat_id:
        """
        return chat_id in self._chats.keys()

    def _load(self):
        with open(self._fp, "r", encoding="utf-8") as file:
            return json.load(file)

    def _dump(self):
        with open(self._fp, "w", encoding="utf-8") as file:
            return json.dump(self._chats, file)
