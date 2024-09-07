"""
Модуль системы оповещений.
"""
from datetime import datetime
from typing import Callable

from asyncio import sleep

from loguru import logger

from rasp_api.schedule import ScheduleImageGenerator

from bot_api.utility import image_to_bytes
from bot_api.chats_connector import Chats


class Notificator:
    """
    Класс работы системы оповещений.
    """
    def __init__(self, chats: Chats, image_generator: ScheduleImageGenerator,  timings: list, cooldown_s: int = 60):
        """
        :param Chats chats: Система подключенных чатов
        :param ScheduleImageGenerator image_generator: генератор изображений с расписанием
        :param list timings: Тайминги отправления
        :param int cooldown_s: Ожидание цикла проверки в секундах
        """
        self._chats = chats
        self._imgen = image_generator
        self._timings = timings
        self._cd = cooldown_s

    async def run(self, sender: Callable, image_loader: Callable):
        """
        :param sender: Функция отправления оповещения
        :param image_loader: Функция загрузки изображения
        """
        logger.info("Активирована система оповещений.")

        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time in self._timings:
                logger.info(f"Оповещение по времени: {current_time}.")

                for chat, group in self._chats.get_chats().items():
                    image = await image_loader(chat, image_to_bytes(await self._imgen.create_daily(group)))
                    logger.info(f"Оповещение для группы: {group}. PeerID: {chat}")
                    await sender(chat, f"{current_time} | Оповещение расписания для группы {group}", image)

            await sleep(self._cd)
