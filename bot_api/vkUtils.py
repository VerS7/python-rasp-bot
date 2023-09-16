# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
from bot_api.simplelogger import loggit


class BotHandler(vk_api.VkApi):
    def __init__(self, token, group_id):
        super().__init__()
        self.token = token
        self.id = group_id
        self.peer_id = None
        self.vk_session = vk_api.VkApi(token=self.token)
        self.botlongpoll = VkBotLongPoll(self.vk_session, self.id)
        self.vk = self.vk_session.get_api()
        self.upload = vk_api.VkUpload(self.vk)

    @loggit
    def send_message(self, message: str):
        """Функция отправки сообщения"""
        try:
            self.vk.messages.send(peer_id=self.peer_id, random_id=get_random_id(), message=message)
        except Exception as exc:
            raise exc

    @loggit
    def send_image(self, attachment, message=None):
        """Функция отправки сообщения с картинкой"""
        try:
            photo = self.upload.photo_messages(attachment)
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            self.vk.messages.send(peer_id=self.peer_id, random_id=get_random_id(), attachment=attachment, message=message)
            return 1
        except Exception as exc:
            raise exc

    @loggit
    def send_images(self, attachs: list, message=None):
        """Функция отправки сообщения с множеством картинок"""
        try:
            attachments = []
            for attach in attachs:
                photo = self.upload.photo_messages(attach)
                owner_id = photo[0]['owner_id']
                photo_id = photo[0]['id']
                access_key = photo[0]['access_key']
                attachments.append(f'photo{owner_id}_{photo_id}_{access_key}')
            self.vk.messages.send(peer_id=self.peer_id, random_id=get_random_id(), attachment=attachments, message=message)
        except Exception as exc:
            raise exc
