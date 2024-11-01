"""
Модуль логики работы асинхронного бота
"""

import asyncio
import json
from os import path
from time import sleep

from typing import Callable, List, Any, Dict, Awaitable
from functools import wraps

from aiovk import API, TokenSession
from aiovk.longpoll import BotsLongPoll
from aiovk.drivers import HttpDriver

from aiohttp import ClientSession, ClientTimeout, TCPConnector, FormData

from loguru import logger

from bot_api.context import Context
from bot_api.command_parser import parse_command
from bot_api.utility import load_txt


GREETING_FILE = path.join(
    path.dirname(path.dirname(path.abspath(__file__))), "files/info.txt"
)

GREETING_TEXT = load_txt(GREETING_FILE)  # Текст с информацией о боте
EXC_DELAY = 10

logger.add(
    path.join(path.dirname(path.dirname(path.abspath(__file__))), "files/debug.log"),
    rotation="2 MB",
)


class ApiAccess:
    """
    Взаимодействие с API
    """

    def __init__(self, access_token: str, pub_id: int) -> None:
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        """
        self._access, self._pubid = access_token, pub_id

        self._loop = asyncio.get_event_loop()

        self._timeout = ClientTimeout()
        self.httpsession = ClientSession(
            connector=TCPConnector(ssl=False, loop=self._loop)
        )

        self.vksession: TokenSession | None = None
        self._driver = HttpDriver(
            loop=self._loop, session=self.httpsession, timeout=self._timeout
        )

        self.api: API | None = None
        self.longpoll: BotsLongPoll | None = None

    def connect(self, access_token: str, pub_id: int) -> None:
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        """
        self.vksession = TokenSession(access_token=access_token, driver=self._driver)
        self.api = API(self.vksession)
        self.longpoll = BotsLongPoll(self.api, group_id=pub_id)

    async def send_message(
        self,
        peer_id: int,
        message: str,
        attachment: List[str] | str | None = None,
        vk_keyboard: str = None,
    ) -> Any:
        """
        Отправляет сообщение по peer_id диалога
        :param str vk_keyboard: JSON в виде строки с VK клавиатурой.
        :param int peer_id: peer id диалога
        :param str message: сообщение
        :param attachment: list/str загруженных на сервер вложений
        :return: message_id сообщения
        """
        param = {"peer_id": peer_id, "message": message}

        _attachment = None

        if vk_keyboard:
            param["keyboard"] = vk_keyboard

        if attachment:
            if isinstance(attachment, list):
                _attachment = ",".join(attachment)
            if isinstance(attachment, str):
                _attachment = attachment
            param["attachment"] = _attachment

        return await self.vksession.send_api_request("messages.send", param)

    async def edit_message(
        self,
        peer_id: int,
        message: str,
        message_id: int,
        attachment: List[str] | str | None = None,
        vk_keyboard: str = None,
    ) -> None:
        """
        Редактирует сообщение по message_id в диалоге по peer_id
        :param str vk_keyboard: JSON в виде строки с VK клавиатурой.
        :param int message_id: айди сообщения для редактирования
        :param int peer_id: peer id диалога
        :param str message: сообщение
        :param attachment: list/str загруженных на сервер вложений
        """
        param = {"peer_id": peer_id, "message": message, "message_id": message_id}

        _attachment = None

        if vk_keyboard:
            param["keyboard"] = vk_keyboard

        if attachment:
            if isinstance(attachment, list):
                _attachment = ",".join(attachment)
            if isinstance(attachment, str):
                _attachment = attachment
            param["attachment"] = _attachment

        await self.vksession.send_api_request("messages.edit", param)

    async def __get_photo_server_url(self, peer_id: int) -> str:
        """
        :param int peer_id: peer_id диалога
        :return: url сервера для загрузки изображений
        """
        response = await self.vksession.send_api_request(
            "photos.getMessagesUploadServer", {"peer_id": peer_id}
        )

        return response["upload_url"]

    async def __upload_image(self, url: str, image: bytes) -> Dict[Any, Any]:
        """
        :param str url: url сервера для загрузки изображений
        :param bytes image: изображение в виде bytes
        :return: response с сервера
        """
        form_data = FormData()
        form_data.add_field("photo", image, filename="rasp_image.png")

        async with self.httpsession.post(url, data=form_data) as response:
            return await response.json(content_type=None)

    async def image_attachments(
        self, peer_id: int, images: List[bytes] | bytes
    ) -> List[str]:
        """
        Создаёт vk attachment из байтов изображений
        :param peer_id: peer_id диалога
        :param images: изображение или список изображений в виде bytes
        :return: vk attachment
        """
        attachments = []
        url = await self.__get_photo_server_url(peer_id)

        if isinstance(images, bytes):
            images = [images]

        for image in images:
            response = await self.__upload_image(url, image)

            if not response.get("photo", None):
                logger.exception("Не удалось загрузить изображение в ВК.")
                continue

            img_response = await self.vksession.send_api_request(
                "photos.saveMessagesPhoto", response
            )

            attachments.append(
                f"photo{img_response[0]['owner_id']}_{img_response[0]['id']}"
            )

        return attachments


class AsyncVkBot(ApiAccess):
    """
    Класс работы ВК бота
    """

    def __init__(
        self,
        access_token: str,
        pub_id: int,
        prefixes: str = "!#",
        admin_ids: List[int] = None,
        services: List[Any] = None,
    ):
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        :param list prefixes: список доступных префиксов для команд
        :param list admin_ids: PeerID админ-чатов
        :param services: Дополнительные сервисы
        """
        super().__init__(access_token, pub_id)

        self.admins = admin_ids
        self.services = services
        self.prefixes = prefixes
        self.commands: Dict[str, Callable] = (
            {}
        )  # словарь {команда: функция} для вызовов из цикла обработки сообщений
        self.events: Dict[str, Callable] = (
            {}
        )  # словарь {тип ивента: функция} для вызовов из цикла обработки сообщений
        self._task_services = []

    async def __commands_worker(self) -> None:
        """
        longpoll-цикл обработки сообщений
        """
        async for event in self.longpoll.iter():
            if event["type"] == "message_new":
                peer = event["object"]["message"][
                    "peer_id"
                ]  # peer_id диалога с новым сообщением
                message = event["object"]["message"]["text"]  # текст сообщения
                payload = event["object"]["message"].get(
                    "payload", None
                )  # Payload сообщения

                command, args = parse_command(message, self.prefixes)

                if command and command in self.commands:
                    await self._handle_command(command, Context(peer, args))

                if payload:
                    await self._handle_payload(payload, peer)

    async def _handle_command(self, command: str, context: Context) -> None:
        """
        Handle command
        """
        if command not in self.commands:
            return

        logger.info(f"Вызвана команда: <{command}>. PeerID: {context.peer}")
        await self._loop.create_task(self.commands[command](context))

    async def _handle_payload(self, payload: str, peer_id: int) -> None:
        """
        Handle payload
        """
        command = json.loads(payload)["command"]
        if command not in self.events:
            return

        logger.info(f"Запущен ивент: <{command}>. PeerID: {peer_id}")
        await self._loop.create_task(self.events[command](peer_id))

    def on_payload(self, payload_type: str) -> Callable:
        """
        Декоратор для объявления ивента в payload-handler
        :param str payload_type: тип ивента
        """

        def _on_payload(func: Callable[[Any], Awaitable]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                await func(*args, **kwargs)

            self.events[payload_type] = wrapper  # Отправка ивента в пул ивентов

            return wrapper

        return _on_payload

    def command(
        self,
        command: str,
        admin: bool = False,
    ) -> Callable:
        """
        Декоратор для объявления команды и ответа на неё
        :param str command: название команды
        :param bool admin: админ-команда или нет. !Привязка идёт к чатам, а не к конкретным юзерам!
        """

        def _command(func: Callable[[Any], Awaitable]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if admin and not args[0].peer in self.admins:
                    logger.exception(
                        f"Вызов админ-команды вне админ-чата. Peer: {args[0].peer}"
                    )
                    return
                await func(*args, **kwargs)

            self.commands[command] = wrapper  # Отправка команды в пул доступных команд

            return wrapper

        return _command

    def run(self):
        """
        Запуск асинхронного бота
        """
        logger.info("Бот запущен.")
        self.connect(self._access, self._pubid)

        while True:
            try:
                self._task_services = [
                    self._loop.create_task(s.run(self))
                    for s in self.services
                    if not s.running
                ]

                self._loop.run_until_complete(
                    asyncio.gather(
                        self._loop.create_task(self.__commands_worker()),
                        *self._task_services,
                    )
                )

            except KeyboardInterrupt:
                logger.info("Отключение...")
                return

            except Exception as e:
                logger.error(e)
                # Остановка сервисов
                for task_service in self._task_services:
                    logger.info(f"Остановка сервиса: {task_service}")
                    task_service.cancel()
                for service in self.services:
                    service.running = False

                logger.info(f"Ожидание: {EXC_DELAY}s.")
                self.connect(self._access, self._pubid)
                sleep(EXC_DELAY)
