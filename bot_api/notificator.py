from typing import Callable
from asyncio import sleep

from rasp_api.Schedule import daily_image
from rasp_api.LoggerConfig import *

from bot_api.Utility import image_to_bytes
from bot_api.chatsConnector import Chats


class Notificator:
    def __init__(self, chats: Chats, timings: list, cooldown_s: int = 60):
        """
        :param Chats chats: Система подключенных чатов
        :param list timings: Тайминги отправления
        :param int cooldown_s: Ожидание цикла проверки в секундах
        """
        self.__chats = chats
        self.__timings = timings
        self.__cd = cooldown_s

    async def run(self, sender: Callable, image_loader: Callable = None):
        """
        :param sender: Функция отправления оповещения
        :param image_loader: Функция загрузки изображения
        """
        logging.info("Активирована система оповещений.")

        while True:
            current_time = datetime.now().strftime("%H:%M")

            if current_time in self.__timings:
                logging.info(f"Оповещение по времени: {current_time}.")
                for chat, group in self.__chats.get_chats().items():
                    if image_loader is not None:
                        image = await image_loader(chat, image_to_bytes(daily_image(group)))
                    else:
                        image = None

                    logging.info(f"Оповещение для группы: {group}. PeerID: {chat}")

                    await sender(chat,
                                 f"{current_time} | повещение расписания для группы {group}",
                                 image)

            await sleep(self.__cd)
