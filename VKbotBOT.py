# -*- coding: utf-8 -*-
import time
from rasp_api import *
from vk_api.bot_longpoll import VkBotEventType


class RaspBot:
    """Тело ВК-бота"""
    def __init__(self):
        print('Бот запущен.')
        print(time.ctime(time.time()))

        """Инициализация необходимых параметров"""
        self.data = DataInit(config="settings.ini",
                             statfile="statistics.csv",
                             infofile="info.txt",
                             commandsfile="comlist.txt")

        Schedule.size = self.data.size                      # Размер изображения расписания
        self.stats = self.data.stats                        # Статистика вызовов
        self.token = self.data.token                        # ВК токен
        self.id = self.data.id                              # ВК айди
        self.bot = vkUtils.BotHandler(self.token, self.id)  # Bothandler
        self.tags = self.data.tags                          # Тэги
        self.grouplist = self.data.grouplist                # Группы
        self.info = self.data.info                          # Информация
        self.comlist = self.data.comlist                    # команды

    @loopexcepter
    @loggit
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
                    self.bot.send_message("\n".join(self.comlist))
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
                        self.bot.send_message(f"Чат с ID:{self.bot.peer_id} успешно добавлен в систему оповещений!")
                    else:
                        self.bot.send_message("Отсутствует номер группы.")

                # Debug Commands
                elif "%checkid" in message.lower():
                    """Посмотреть айди чата"""
                    self.bot.send_message(self.bot.peer_id)

                elif "%manualstart" in message.lower():
                    """Ручной запуск оповещения"""
                    if self.bot.peer_id == 406579945:
                        manual = Annunciator(self.bot)
                        manual.chats_send()


if __name__ == '__main__':
    VKbot = RaspBot()
    VKbot.main()
