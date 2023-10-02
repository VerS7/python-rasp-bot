import logging

from aiovk import API, TokenSession
from aiovk.longpoll import BotsLongPoll
from aiohttp import ClientSession, FormData

from typing import Callable, Union, List

from time import sleep

from bot_api.commandParser import Command
from rasp_api.LoggerConfig import *

import asyncio

EXC_DELAY = 10


class AsyncVkBot:
    def __init__(self, access_token: str, pub_id: int, prefixes: str = "!#"):
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        :param prefixes: список доступных префиксов для команд
        """
        self.__access, self.__pubid = access_token, pub_id

        self.session: TokenSession = None
        self.api: API = None
        self.longpoll: BotsLongPoll = None

        self.__prefixes = prefixes

        self.__commands = {}  # словарь {команда: функция} для вызовов функций из цикла обработки сообщений

    def __connect(self, access_token: str, pub_id: int):
        """
        :param str access_token: токен доступа группы ВК
        :param int pub_id: id группы ВК
        """
        self.session = TokenSession(access_token=access_token)
        self.api = API(self.session)
        self.longpoll = BotsLongPoll(self.api, group_id=pub_id)

    async def __main(self):
        """
        main бесконечный longpoll цикл обработки сообщений
        """
        async for event in self.longpoll.iter():
            if event["type"] == "message_new":

                peer = event["object"]["message"]["peer_id"]  # peer_id диалога с новым сообщением
                message = event["object"]["message"]["text"]  # текст сообщения

                command = Command(message, self.__prefixes)  # обработка сообщения
                if command.isCommand() and command.command in self.__commands.keys():  # проверка на наличие команды
                    asyncio.create_task(self.__commands[command.command](peer, command.args))
                    logging.info(f"Выполнена команда [{command.command} ({command.args})] PeerID: {peer}")

    async def send_message(self, peer_id: str, message: str, attachment: Union[list, str, None] = None) -> int:
        """
        Отправляет сообщение по peer_id диалога
        :param int peer_id: peer id диалога
        :param str message: сообщение
        :param attachment: list/str загруженных на сервер вложений
        :return: message_id сообщения
        """
        param = {"peer_id": peer_id, "message": message}

        if attachment:
            if isinstance(attachment, list):
                _attachment = ",".join(attachment)
            if isinstance(attachment, str):
                _attachment = attachment
            param["attachment"] = _attachment

        return await self.session.send_api_request("messages.send", param)

    async def edit_message(self, peer_id: str, message: str, message_id: int,
                           attachment: Union[list, str, None] = None) -> None:
        """
        Редактирует сообщение по message_id в диалоге по peer_id
        :param int message_id: айди сообщения для редактирования
        :param int peer_id: peer id диалога
        :param str message: сообщение
        :param attachment: list/str загруженных на сервер вложений
        """
        param = {"peer_id": peer_id, "message": message, "message_id": message_id}

        if attachment:
            if isinstance(attachment, list):
                _attachment = ",".join(attachment)
            if isinstance(attachment, str):
                _attachment = attachment
            param["attachment"] = _attachment

        await self.session.send_api_request("messages.edit", param)

    async def __get_photo_server_url(self, peer_id: int) -> str:
        """
        :param int peer_id: peer_id диалога
        :return: url сервера для загрузки изображений
        """
        response = await self.session.send_api_request("photos.getMessagesUploadServer", {"peer_id": peer_id})
        return response["upload_url"]

    async def __upload_image(self, url: str, image: bytes) -> dict:
        """
        :param str url: url сервера для загрузки изображений
        :param bytes images: изображение в виде bytes
        :return: response с сервера
        """
        form_data = FormData()
        form_data.add_field('photo', image, filename=f'rasp_image.png')

        async with ClientSession() as session:
            async with session.post(url, data=form_data) as response:
                return await response.json(content_type=None)

    async def image_attachments(self, peer_id: int, images: Union[List[bytes], bytes]) -> List[str]:
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
            img_response = await self.session.send_api_request("photos.saveMessagesPhoto", response)
            attachments.append(f"photo{img_response[0]['owner_id']}_{img_response[0]['id']}")

        return attachments

    def command(self, command: Union[str, None] = None,
                replaceable: bool = False,
                placeholder: Union[str, None] = None,
                admin: bool = False) -> Callable:
        """
        Декоратор для объявления команды и ответа на неё
        :param str command: команда, которую слушает event listener
        :param bool replaceable: изменяется ли сообщение в процессе обработки
        :param str placeholder: сообщение, которое будет изменено
        :param bool admin: админ-команда или нет
        :return: command-wrapper
        """

        def __command(__func):
            async def __wrapper(*args, **kwargs):
                # Основная логика
                if admin:  # Если сообщение от админа
                    raise NotImplementedError

                attachment = None

                if replaceable and placeholder:  # Если есть placeholder и сообщение replaceable
                    message_id = await self.send_message(peer_id=args[0], message=placeholder)
                    result = await __func(*args, **kwargs)
                    if message_id != 0:
                        if len(result) == 3:
                            attachment = await self.image_attachments(result[0], result[2])
                        return await self.edit_message(peer_id=args[0], message=result[1],
                                                       message_id=message_id, attachment=attachment)
                result = await __func(*args, **kwargs)
                if len(result) == 3:
                    attachment = await self.image_attachments(result[0], result[2])

                return await self.send_message(peer_id=result[0], message=result[1], attachment=attachment)

            self.__commands[command] = __wrapper  # Отправка команды в пул доступных команд

            return __wrapper

        return __command

    def run(self):
        """
        Запуск асинхронного бота
        """
        logging.info(msg="Бот запущен.")
        self.__connect(self.__access, self.__pubid)
        while True:
            try:
                loop = asyncio.get_event_loop()
                task = loop.create_task(self.__main())
                loop.run_until_complete(task)

            except KeyboardInterrupt:
                logging.info(msg=f"Отключение...")

            except Exception as exc:
                logging.error(exc)
                logging.info(msg=f"Ожидание: {EXC_DELAY}s.")
                self.__connect(self.__access, self.__pubid)
                sleep(EXC_DELAY)
