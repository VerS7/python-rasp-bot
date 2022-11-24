# -*- coding: utf-8 -*-
import time
from rasp_api import *
from vk_api.bot_longpoll import VkBotEventType


class RaspBot:
    """Тело ВК-бота"""
    def __init__(self):
        print("Бот запущен.")
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
        self.comlist = self.data.comlist                    # Команды

        self.cmndHanler = commandHandler(self.bot,          # BotHandler
                                         self.stats,        # Статистика вызовов
                                         self.info,         # Информация
                                         self.grouplist,    # Группы
                                         self.comlist,      # Команды
                                         self.tags)         # тэги

    @loopexcepter
    @loggit
    def main(self):
        """Цикл прочитки сообщений ботом"""
        for event in self.bot.botlongpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.cmndHanler.set_event(event)
                self.cmndHanler.set_peer(event)

                if self.cmndHanler.validator.get_command() == "команды":
                    """Запрос информации о боте"""
                    self.cmndHanler.send_info()

                if self.cmndHanler.validator.get_command() == "группы":
                    """Запрос доступных групп"""
                    self.cmndHanler.send_groups()

                if self.cmndHanler.validator.get_command() == "расп":
                    """Запрос расписания"""
                    self.cmndHanler.send_rasp()

                if self.cmndHanler.validator.get_command() == "нрасп":
                    """Запрос недельного расписания"""
                    self.cmndHanler.send_weekrasp()

                if self.cmndHanler.validator.get_command() == "орасп":
                    """Запрос основного расписания"""
                    self.cmndHanler.send_mainrasp()

                if self.cmndHanler.validator.get_command() == "оповещение":
                    """Запрос на добавление в систему оповещений"""
                    self.cmndHanler.add_to_annons()

                if self.cmndHanler.validator.get_command() == "checkid":
                    pass

                if self.cmndHanler.validator.get_command() == "manualstart":
                    pass

                # # Debug Commands
                # elif "%checkid" in message.lower():
                #     """Посмотреть айди чата"""
                #     self.bot.send_message(self.bot.peer_id)
                #
                # elif "%manualstart" in message.lower():
                #     """Ручной запуск оповещения"""
                #     if self.bot.peer_id == 406579945:
                #         manual = Annunciator(self.bot)
                #         manual.chats_send()


if __name__ == '__main__':
    VKbot = RaspBot()
    VKbot.main()
