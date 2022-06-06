# -*- coding: utf-8 -*-
import vk_api
import time
import configparser
from BotUtils import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


class RaspBot:
    """Код работы с ВК"""
    def __init__(self):
        """Инициализация необходимых параметров"""
        self.config = configparser.ConfigParser()
        self.config.read("settings.ini")
        """Подключение к сообществу по токену и ID"""
        self.token = self.config['bot']['token']
        self.id = self.config['bot']['pubid']
        self.vk_session = vk_api.VkApi(token=self.token)
        self.botlongpoll = VkBotLongPoll(self.vk_session, self.id)
        self.vk = self.vk_session.get_api()
        self.upload = vk_api.VkUpload(self.vk)

        """Открываем необходимые файлы"""
        try:
            self.tags = GatherTags.tagsprettify()
            self.grouplist = GatherTags.grouplist_create()
            with open("info.txt", "r", encoding="utf-8") as info:
                self.info = info.read()
            with open("comlist.txt", "r", encoding="utf-8") as comlist:
                self.comlist = [row.strip() for row in comlist]
        except Exception as e:
            print(e)
            print('Не удалось получить доступ к необходимым файлам.')
            exit()

    def main(self):
        """Цикл прочитки сообщений ботом"""
        try:
            for event in self.botlongpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    message = event.obj['message']['text']
                    peer_id = event.obj['message']['peer_id']

                    if self.comlist[0] in message.lower():
                        """Запрос информации о боте"""
                        self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message=self.info)

                    elif self.comlist[1] in message.lower():
                        """Запрос доступных групп"""
                        self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="\n".join(self.grouplist))

                    elif self.comlist[4] in message.lower():
                        """Запрос расписания картинкой"""
                        try:
                            if len(message.split()) == 2:
                                if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Подождите, идёт обработка.")
                                    Schedule.reading_img(message.split()[1], "raspback.png")
                                    photo = self.upload.photo_messages('rasp_pic.png')
                                    owner_id = photo[0]['owner_id']
                                    photo_id = photo[0]['id']
                                    access_key = photo[0]['access_key']
                                    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), attachment=attachment, message='Расписание для группы {0}'.format(message.split()[1]))
                                else:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Произошла ошибка.")
                            else:
                                self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Отсутствует номер группы.")
                        except Exception as e:
                            print(e)

                    elif self.comlist[2] in message.lower():
                        """Запрос недельного расписания в картинках"""
                        try:
                            if len(message.split()) == 2:
                                Util.img_clear('cg/*')
                                if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Подождите, идёт обработка.")
                                    Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags)
                                    attachment = []
                                    for image in glob.glob('cg/*.png'):
                                        photo = self.upload.photo_messages(image)
                                        owner_id = photo[0]['owner_id']
                                        photo_id = photo[0]['id']
                                        access_key = photo[0]['access_key']
                                        attachment.append(f'photo{owner_id}_{photo_id}_{access_key}')
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), attachment=attachment, message='Недельное расписание для группы {0}'.format(message.split()[1]))
                                else:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message='Произошла ошибка.')
                            else:
                                self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Отсутствует номер группы.")
                        except Exception as e:
                            print(e)

                    elif self.comlist[3] in message.lower():
                        """Запрос основного расписания в картинках"""
                        try:
                            if len(message.split()) == 2:
                                Util.img_clear('bg/*')
                                if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Подождите, идёт обработка.")
                                    Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags, urltype='bg')
                                    attachment = []
                                    for image in glob.glob('bg/*.png'):
                                        photo = self.upload.photo_messages(image)
                                        owner_id = photo[0]['owner_id']
                                        photo_id = photo[0]['id']
                                        access_key = photo[0]['access_key']
                                        attachment.append(f'photo{owner_id}_{photo_id}_{access_key}')
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), attachment=attachment, message='Основное расписание для группы {0}'.format(message.split()[1]))
                                else:
                                    self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message='Произошла ошибка.')
                            else:
                                self.vk.messages.send(peer_id=peer_id, random_id=get_random_id(), message="Отсутствует номер группы.")
                        except Exception as e:
                            print(e)

        except Exception as e:
            print(e)
            print(time.ctime(time.time()))


if __name__ == '__main__':
    VKbot = RaspBot()
    print('Бот запущен.')
    print(time.ctime(time.time()))
    VKbot.main()