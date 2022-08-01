# -*- coding: utf-8 -*-
import vk_api
import logging
import os
import shutil
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
from .Util import Util


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
        logging.basicConfig(filename='Errors.log')

    def send_message(self, message: str) -> int:
        """Функция отправки сообщения"""
        try:
            self.vk.messages.send(peer_id=self.peer_id, random_id=get_random_id(), message=message)
            return 1
        except Exception as exc:
            logging.error(exc)
            raise exc

    def send_image(self, attachment: str, message=None) -> int:
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
            logging.error(exc)
            raise exc

    def send_images(self, attachs: list, message=None) -> int:
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
            return 1
        except Exception as exc:
            logging.error(exc)
            raise exc
