# -*- coding: utf-8 -*-
"""
Модуль системы оповещений.
"""
from typing import Callable, Union, Any
from asyncio import sleep

from rasp_api.schedule import daily_image, is_empty
from rasp_api.parsing import parse_request, get_daily, URL_DAILY
from rasp_api.log_conf import *

from bot_api.utility import image_to_bytes
from bot_api.chats_connector import Chats


class Notificator:
    """
    Класс работы системы оповещений.
    """
    def __init__(self, chats: Chats, timings: list, cooldown_s: int = 60):
        """
        :param Chats chats: Система подключенных чатов
        :param list timings: Тайминги отправления
        :param int cooldown_s: Ожидание цикла проверки в секундах
        """
        self.__chats = chats
        self.__timings = timings
        self.__cd = cooldown_s

    async def run(self, sender: Callable, image_loader: Callable):
        """
        :param sender: Функция отправления оповещения
        :param image_loader: Функция загрузки изображения
        """
        logging.info("Активирована система оповещений.")

        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time in self.__timings:
                logging.info(f"Оповещение по времени: {current_time}.")
                parsed = parse_request(URL_DAILY)
                for chat, group in self.__chats.get_chats().items():
                    if is_empty(get_daily(group, parsed)):
                        image = await image_loader(chat,
                                                   image_to_bytes(daily_image(group, parsed, 0.7)))
                        logging.info(f"Оповещение для группы: {group}. PeerID: {chat}")
                        await sender(chat,
                                     f"{current_time} | повещение расписания для группы {group}",
                                     image)
                    else:
                        logging.info(f"Расписание для группы {group} Пустое.")
            await sleep(self.__cd)
