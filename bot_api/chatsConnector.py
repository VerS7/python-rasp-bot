from typing import Union
import json

CHATS_PATH = "../files/chats.json"


class Chats:
    def __init__(self, path: str = CHATS_PATH):
        self.__path = path
        self.chats: dict = self.__load_json()

    def add_group(self, chat_id: int, groupname: str):
        """
        Сохраняет значение чат: группа
        :param str chat_id: айди чата
        :param str groupname: имя группы
        """
        self.chats[chat_id] = groupname

    def remove_chat(self, chat: str) -> Union[str, None]:
        """
        Удаляет конкретный чат из сохранённых чатов
        :param str chat: id чата
        :return: удалённая группа или None в случае отсутствия
        """
        return self.chats.pop(chat, None)

    def __load_json(self):
        with open(self.__path, "r", encoding="utf-8") as file:
            return json.load(file)

    def __dump_json(self):
        with open(self.__path, "w", encoding="utf-8") as file:
            return json.dump(self.chats, file)