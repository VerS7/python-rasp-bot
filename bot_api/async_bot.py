"""
Модуль логики работы асинхронного бота
"""

import asyncio
import json
from os import path
from time import sleep

from typing import Callable, Union, List, Any
from functools import wraps

from aiovk import API, TokenSession
from aiovk.longpoll import BotsLongPoll
from aiovk.drivers import HttpDriver

from aiohttp import ClientSession, ClientTimeout, TCPConnector, FormData

from loguru import logger

from bot_api.command_parser import Command
from bot_api.keyboard import get_keyboard_string, BASIC_KEYBOARD

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

    def __init__(self, access_token: str, pub_id: int):
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

    def connect(self, access_token: str, pub_id: int):
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        """
        self.vksession = TokenSession(access_token=access_token, driver=self._driver)
        self.api = API(self.vksession)
        self.longpoll = BotsLongPoll(self.api, group_id=pub_id)

    async def send_message(
        self,
        peer_id: str,
        message: str,
        attachment: Union[list, str, None] = None,
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
        peer_id: str,
        message: str,
        message_id: int,
        attachment: Union[list, str, None] = None,
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

    async def __upload_image(self, url: str, image: bytes) -> dict:
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
        self, peer_id: int, images: Union[List[bytes], bytes]
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

            if response.get("error_code", None):
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
        admin_ids: list = None,
        services: list = None,
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
        self.commands = (
            {}
        )  # словарь {команда: функция} для вызовов из цикла обработки сообщений

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

                command = Command(message, self.prefixes)  # обработка сообщения
                if command.is_command() and command.command in self.commands:
                    await self.run_command(command.command, peer, command.args)

                if payload:
                    if json.loads(payload)["command"] == "start":
                        await self.send_message(
                            peer,
                            message=GREETING_TEXT,
                            vk_keyboard=get_keyboard_string(BASIC_KEYBOARD),
                        )
                    else:
                        await self.run_command(json.loads(payload)["command"], peer)

    async def run_command(self, command: str, peer_id: int, args: list = None) -> None:
        """
        Создаёт async задачу по команде
        :param str command: команда, по которой будет выполнена функция из пула команд.
        :param int peer_id:
        :param list args: Аргументы команды или None
        """
        logger.info(f"Вызвана команда: <{command}>({args}). PeerID: {peer_id}")
        await self._loop.create_task(self.commands[command](peer_id, args))

    def command(
        self,
        command: Union[str, None] = None,
        placeholder: Union[str, None] = None,
        keyboard: str = None,
        admin: bool = False,
    ) -> Callable:
        """
        Декоратор для объявления команды и ответа на неё
        :param str command: команда, которую слушает event listener
        :param str keyboard: клавиатура
        :param str placeholder: сообщение, которое будет изменено
        :param bool admin: админ-команда или нет. !Привязка идёт к чатам, а не к конкретным юзерам!
        :return: command-wrapper
        """

        def __command(__func: Callable):
            @wraps(__func)
            async def __wrapper(*args, **kwargs):
                attach = None  # attachment (изображение)
                message_id = 0  # Базовый message id
                peer = args[0]  # peer id, возвращаемый командой
                keyboard_ = None  # ВК клавиатура

                if str(peer)[0] != 2:
                    keyboard_ = keyboard

                logger.info(
                    f"Вызвана функция: {__func.__name__}({args[1::]}). PeerID: {peer}"
                )

                if (
                    admin and not args[0] in self.admins
                ):  # Если админ-команда не от админа
                    return None

                if placeholder:  # Если есть placeholder
                    message_id = await self.send_message(
                        peer_id=peer, message=placeholder, vk_keyboard=keyboard_
                    )

                result = await __func(*args, **kwargs)

                if placeholder and message_id != 0:
                    if len(result) == 3:
                        attach = await self.image_attachments(peer, result[2])
                        if not attach:
                            return await self.edit_message(
                                peer_id=peer,
                                message="Не удалось загрузить расписание. Попробуйте ещё раз.",
                                message_id=message_id,
                            )

                    return await self.edit_message(
                        peer_id=peer,
                        message=result[1],
                        message_id=message_id,
                        attachment=attach,
                    )

                if placeholder and message_id == 0:
                    logger.info(
                        f"MessageID для замены сообщения: {message_id}. Невозможно заменить сообщение."
                    )

                if len(result) == 3:
                    attach = await self.image_attachments(peer, result[2])

                return await self.send_message(
                    peer_id=peer,
                    message=result[1],
                    attachment=attach,
                    vk_keyboard=keyboard_,
                )

            self.commands[command] = (
                __wrapper  # Отправка команды в пул доступных команд
            )

            return __wrapper

        return __command

    def run(self):
        """
        Запуск асинхронного бота
        """
        logger.info("Бот запущен.")
        self.connect(self._access, self._pubid)

        while True:
            try:
                services = [
                    self._loop.create_task(s.run(self))
                    for s in self.services
                    if not s.running
                ]
                # print(services)
                self._loop.run_until_complete(
                    asyncio.gather(
                        self._loop.create_task(self.__commands_worker()), *services
                    )
                )

            except KeyboardInterrupt:
                logger.info("Отключение...")
                return

            except Exception as e:
                raise e
                logger.error(e)
                logger.info(f"Ожидание: {EXC_DELAY}s.")
                self.connect(self._access, self._pubid)
                sleep(EXC_DELAY)
