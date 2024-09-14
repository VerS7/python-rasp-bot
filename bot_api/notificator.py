"""
Модуль системы оповещений.
"""
from datetime import datetime
from typing import Callable, List, Any, Tuple

from asyncio import sleep

from loguru import logger

from rasp_api.schedule import ScheduleImageGenerator

from bot_api.utility import image_to_bytes
from bot_api.chats_connector import Chats


class Notificator:
    """
    Класс работы системы оповещений.
    """
    def __init__(self, chats: Chats, image_generator: ScheduleImageGenerator,  timings: list, cooldown_s: int = 30):
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
                scheduler = TaskScheduler()
                logger.info(f"Оповещение по времени: {current_time} запущено.")

                for chat, group in self._chats.get_chats().items():
                    scheduler.add(self._send, chat, group, sender, image_loader, current_time)

                await scheduler.execute()
                await sleep(60)

            await sleep(self._cd)

    async def _send(self, chat: str, group: str, sender: Callable, image_loader: Callable, current_time: str) -> None:
        image = await image_loader(chat, image_to_bytes(await self._imgen.create_daily(group)))
        logger.info(f"Оповещение для группы: {group}. PeerID: {chat}")
        await sender(chat, f"{current_time} | Оповещение расписания для группы {group}", image)


class TaskScheduler:
    def __init__(self):
        self._signal = False
        self._callables: List[Tuple[Callable, Tuple[Any, ...]]] = []

    def add(self, callback: Callable, *args) -> None:
        self._callables.append((callback, args))

    async def execute(self) -> None:
        for callback, args in self._callables:
            await callback(*args)
        self._signal = True
