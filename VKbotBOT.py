# -*- coding: utf-8 -*-
import time
import configparser
from BotUtils import *
from vkUtils import BotHandler
from vk_api.bot_longpoll import VkBotEventType


class RaspBot:
    """Код работы с ВК"""
    def __init__(self):
        """Инициализация необходимых параметров"""
        self.config = configparser.ConfigParser()
        self.config.read("settings.ini")
        Schedule.size = int(self.config['image']['width']), int(self.config['image']['length'])
        """Токен и ID сообщества"""
        self.token = self.config['bot']['token']
        self.id = self.config['bot']['pubid']
        """Подключение бота из класса BotHandler"""
        self.bot = BotHandler(self.token, self.id)
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
        for event in self.bot.botlongpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.obj['message']['text']
                self.bot.peer_id = event.obj['message']['peer_id']

                if self.comlist[0] in message.lower():
                    """Запрос информации о боте"""
                    self.bot.send_message(self.info)

                elif self.comlist[1] in message.lower():
                    """Запрос доступных групп"""
                    self.bot.send_message("\n".join(self.grouplist))

                elif self.comlist[4] in message.lower():
                    """Запрос расписания картинкой"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            Schedule.reading_img(message.split()[1], "raspback.png")
                            self.bot.send_image('temp/rasp.png', 'Расписание для группы {0}'.format(message.split()[1]))
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif self.comlist[2] in message.lower():
                    """Запрос недельного расписания в картинках"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags)
                            self.bot.send_images(glob.glob('temp/cg/*.png'), 'Недельное расписание для группы {0}'.format(message.split()[1]))
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif self.comlist[3] in message.lower():
                    """Запрос основного расписания в картинках"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags, urltype='bg')
                            self.bot.send_images(glob.glob('temp/bg/*.png'), 'Основное расписание для группы {0}'.format(message.split()[1]))
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")


if __name__ == '__main__':
    VKbot = RaspBot()
    print('Бот запущен.')
    print(time.ctime(time.time()))
    VKbot.main()
