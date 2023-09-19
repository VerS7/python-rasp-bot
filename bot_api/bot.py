from aiovk import API, TokenSession
from aiovk.longpoll import BotsLongPoll
from typing import Union, List
from aiohttp import ClientSession, FormData
from utility import *
import asyncio


class AsyncVkBot:
    def __init__(self, access_token: str, pub_id: int):
        self.session = TokenSession(access_token=access_token)
        self.api = API(self.session)
        self.longpoll = BotsLongPoll(self.api, group_id=pub_id)

        self.__commands = {}

    async def __main(self):
        async for event in self.longpoll.iter():
            if event["type"] == "message_new":

                peer = event["object"]["message"]["peer_id"]

                if event["object"]["message"]["text"] == "!t":
                    images = image_to_bytes([Image.open("../files/raspback.png"), Image.open("../files/test.jpg")])
                    att = await self.image_attachments(peer, images)
                    await self.send_message(peer, "тестовое изображение", attachment=att)

                message = event["object"]["message"]["text"]
                if any(message.startswith(prefix) for prefix in ["%", "!", "^", "@"]):
                    if message.split()[0] in self.__commands.keys():
                        self.__commands[message.split()[0]](peer, message)

    async def send_message(self, peer_id: str, message: str, attachment: Union[list, str, None] = None) -> int:
        """
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

    def run(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.__main())
        loop.run_until_complete(task)

    def command(self, command: Union[str, None] = None,
                replaceable: bool = False,
                placeholder: Union[str, None] = None,
                admin: bool = False):
        """
        :param str command: команда, которую слушает event listener
        :param bool replaceable: изменяется ли сообщение в процессе обработки
        :param str placeholder: сообщение, которое будет изменено
        :param bool admin: админ-команда или нет
        :return: command-wrapper
        """
        def __command(__func):
            self.__commands[command] = __func

            def __wrapper(*args, **kwargs):
                # TODO: плейсхолдер реализовать
                print(args)
                # self.send_message(args[0], args[1])
                #
                return __func(*args, **kwargs)

            return __wrapper

        return __command


t = "b43c55878dc7efb2ba857f47d389298d3aae540f72eba893c70eedc1e30109f50e770f3f45b052f180a04"
p = 209586297
a = AsyncVkBot(t, p)


@a.command(command="!тест")
def send_daily(peer, message):
    print(peer, message)
    print("выполнено")


a.run()
