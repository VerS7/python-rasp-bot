"""
Модуль системы оповещений.
"""

from abc import ABC, abstractmethod
from asyncio import sleep
from datetime import datetime
from typing import Callable, List, Any, Tuple, Awaitable

from loguru import logger

from bot_api.chats_connector import Chats
from bot_api.utility import image_to_bytes
from bot_api.async_bot import ApiAccess
from rasp_api.schedule import ScheduleImageGenerator


class AbstractBotService(ABC):
    """Абстрактный сервис для бота"""

    running = False

    @abstractmethod
    async def run(self, bot) -> None:
        pass


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


class NotificatorService(AbstractBotService):
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
        self._img = image_generator
        self._timings = timings
        self._cd = cooldown_s

    async def run(self, bot: ApiAccess) -> None:
        """
        Запуск системы оповещений
        """
        logger.info("Активирована система оповещений.")
        self.running = True

        while True:
            current_time = datetime.now().strftime("%H:%M")

            if current_time in self._timings:
                scheduler = AsyncTaskScheduler()
                logger.info(f"Оповещение по времени: {current_time} запущено.")

                for chat_peer, group_id in self._chats.get_chats().items():
                    scheduler.add(
                        self._send_notice,
                        chat_peer,
                        group_id,
                        bot,
                        current_time,
                    )

                await scheduler.execute(on_complete=lambda: sleep(60))

            await sleep(self._cd)

    async def _send_notice(
        self, chat_peer: str, group_id: str, bot: ApiAccess, current_time: str
    ) -> None:
        image = await bot.image_attachments(
            int(chat_peer), image_to_bytes(await self._img.create_daily(group_id))
        )
        logger.info(f"Оповещение для группы: {group_id}. PeerID: {chat_peer}")

        await bot.send_message(
            chat_peer,
            f"{current_time} | Оповещение расписания для группы {group_id}",
            image,
        )
