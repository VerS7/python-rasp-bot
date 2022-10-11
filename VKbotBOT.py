# -*- coding: utf-8 -*-
import time
import configparser
from rasp_api import *
from vk_api.bot_longpoll import VkBotEventType


class RaspBot:
    """Код работы с ВК"""
    def __init__(self):
        print('Бот запущен.')
        print(time.ctime(time.time()))
        """Инициализация необходимых параметров"""
        self.config = configparser.ConfigParser()
        self.config.read("settings.ini")
        Schedule.size = int(self.config['image']['width']), int(self.config['image']['length'])
        self.stats = StatisticsHandler('statistics.csv')
        """Токен и ID сообщества"""
        self.token = self.config['bot']['token']
        self.id = self.config['bot']['pubid']
        """Подключение бота из класса BotHandler"""
        self.bot = vkUtils.BotHandler(self.token, self.id)
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
                    self.stats.write_stats(event)

                elif self.comlist[1] in message.lower():
                    """Запрос доступных групп"""
                    self.bot.send_message("\n".join(self.grouplist))
                    self.stats.write_stats(event)

                elif self.comlist[4] in message.lower():
                    """Запрос расписания картинкой"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            img = Util.pilobj_to_bytes(Schedule.reading_img(message.split()[1], "raspback.png"))
                            self.bot.send_image(img, 'Расписание для группы {0}'.format(message.split()[1]))
                            self.stats.write_stats(event)
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif self.comlist[2] in message.lower():
                    """Запрос недельного расписания в картинках"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            imgs = Util.pilobjs_to_bytes(Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags))
                            self.bot.send_images(imgs, 'Недельное расписание для группы {0}'.format(message.split()[1]))
                            self.stats.write_stats(event)
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif self.comlist[3] in message.lower():
                    """Запрос основного расписания в картинках"""
                    if len(message.split()) == 2:
                        if GatherTags.groupname_validation(message.split()[1], self.grouplist) is True:
                            self.bot.send_message("Подождите, идёт обработка.")
                            imgs = Util.pilobjs_to_bytes(Schedule.weekreading_img(message.split()[1], "raspback.png", tags=self.tags, urltype='bg'))
                            self.bot.send_images(imgs, 'Основное расписание для группы {0}'.format(message.split()[1]))
                            self.stats.write_stats(event)
                        else:
                            self.bot.send_message("Произошла ошибка.")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif self.comlist[6] in message.lower():
                    """Добавить чат с запроса в систему оповещений"""
                    if len(message.split()) == 2:
                        Annunciator.add_to_chatlist(Annunciator.chats_read(), self.bot.peer_id, message.split()[1])
                        self.bot.send_message(f"Чат с ID:{self.bot.peer_id} успешно добавлен в систему оповещний!")
                        #x = Annunciator(self.bot)
                        #x.run()
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                elif "!checkid" in message.lower():
                    """Check chat_id"""
                    self.bot.send_message(self.bot.peer_id)


if __name__ == '__main__':
    VKbot = RaspBot()
    VKbot.main()


