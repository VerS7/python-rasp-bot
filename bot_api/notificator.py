"""
Модуль системы оповещений.
"""

from datetime import datetime
from typing import Callable, List, Any, Tuple, Awaitable
from asyncio import sleep

from loguru import logger

from rasp_api.schedule import ScheduleImageGenerator
from bot_api.utility import image_to_bytes
from bot_api.chats_connector import Chats


class Notificator:
    """Реализация работы системы оповещений"""

    def __init__(
        self,
        chats: Chats,
        image_generator: ScheduleImageGenerator,
        timings: list,
        cooldown_s: int = 30,
    ):
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

    async def run(self, message_callback: Callable, image_loader_callback: Callable):
        """
        :param message_callback: Функция отправления оповещения
        :param image_loader_callback: Функция загрузки изображения
        """
        logger.info("Активирована система оповещений.")

        while True:
            current_time = datetime.now().strftime("%H:%M")

            if current_time in self._timings:
                scheduler = AsyncTaskScheduler()
                logger.info(f"Оповещение по времени: {current_time} запущено.")

                for chat, group in self._chats.get_chats().items():
                    scheduler.add(
                        self._send,
                        chat,
                        group,
                        message_callback,
                        image_loader_callback,
                        current_time,
                    )

                await scheduler.execute()
                await sleep(60)

            await sleep(self._cd)

    async def _send(
        self,
        chat: str,
        group: str,
        sender: Callable,
        image_loader: Callable,
        current_time: str,
    ) -> None:
        image = await image_loader(
            chat, image_to_bytes(await self._imgen.create_daily(group))
        )
        logger.info(f"Оповещение для группы: {group}. PeerID: {chat}")
        await sender(
            chat, f"{current_time} | Оповещение расписания для группы {group}", image
        )


class AsyncTaskScheduler:
    """Реализация добавления асинхронных функций в пачку и их запуск"""

    def __init__(self):
        self._callbacks: List[Tuple[Callable[..., Awaitable], Tuple[Any, ...]]] = []

    def add(self, callback: Callable[..., Awaitable], *args) -> None:
        """
        Добавляет callback в пачку для исполнения
        :param callback:
        :param args:
        :return:
        """
        self._callbacks.append((callback, args))

    async def execute(self, on_complete: Callable[..., Awaitable] = None) -> None:
        """
        Запускает исполнение пачки добавленных callback'ов
        :param on_complete: асинхронная функция на окончании выполнения
        """
        for callback, args in self._callbacks:
            await callback(*args)

        if on_complete:
            await on_complete()
