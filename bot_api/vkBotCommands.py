# -*- coding: utf-8 -*-
from .vkUtils import BotHandler
from .statistics import StatisticsHandler
from .msgValidator import Validator
from .Schedule import Schedule
from .Util import Util
from .annunciator import Annunciator
from .simplelogger import loggit, loggitf


class commandHandler:
    """"""
    def __init__(self, botHandler: BotHandler, statistics: StatisticsHandler, info, grouplist, commands, tags):
        """VK message event"""
        self.event = None
        """Bot handler"""
        self.bot = botHandler
        """Statistics handler"""
        self.stats = statistics
        """Data"""
        self.info = info
        self.tags = tags
        self.grouplist = grouplist
        self.commands = commands
        self.validator = Validator(self.commands, self.grouplist)

    def set_peer(self, event):
        """Установка peer id"""
        self.bot.peer_id = event.obj['message']['peer_id']

    def set_event(self, event):
        """Установка VK event"""
        self.validator.event = event
        self.event = event

    @loggit
    def send_info(self):
        """Отправка информации о боте"""
        self.bot.send_message(self.info)
        self.stats.write_stats(self.event)

    @loggit
    def send_groups(self):
        """Отправка доступных для запроса групп"""
        self.bot.send_message("\n".join(self.grouplist))
        self.stats.write_stats(self.event)

    def send_rasp(self):
        """Отправка расписания"""
        if self.validator.get_groupname() is not None:
            self.bot.send_message("Подождите, идёт обработка.")
            img = Util.pilobj_to_bytes(Schedule.reading_img(self.validator.get_groupname(), "raspback.png"))
            self.bot.send_image(img, "Расписание для группы {0}".format(self.validator.get_groupname()))
            self.stats.write_stats(self.event)
        else:
            self.bot.send_message("Неверный номер группы.")

    def send_weekrasp(self):
        """Отправка недельного расписания"""
        if self.validator.get_groupname() is not None:
            self.bot.send_message("Подождите, идёт обработка.")
            imgs = Util.pilobjs_to_bytes(Schedule.weekreading_img(self.validator.get_groupname(), "raspback.png", tags=self.tags))
            self.bot.send_images(imgs, 'Недельное расписание для группы {0}'.format(self.validator.get_groupname()))
            self.stats.write_stats(self.event)
        else:
            self.bot.send_message("Отсутствует номер группы.")

    def send_mainrasp(self):
        """Отправка основного расписания"""
        if self.validator.get_groupname() is not None:
            self.bot.send_message("Подождите, идёт обработка.")
            imgs = Util.pilobjs_to_bytes(Schedule.weekreading_img(self.validator.get_groupname(), "raspback.png", tags=self.tags, urltype='bg'))
            self.bot.send_images(imgs, 'Основное расписание для группы {0}'.format(self.validator.get_groupname()))
            self.stats.write_stats(self.event)
        else:
            self.bot.send_message("Отсутствует номер группы.")

    @loggit
    def add_to_annons(self):
        """Добавить чат в систему оповещений"""
        if self.validator.get_groupname() is not None:
            if str(self.bot.peer_id) not in Annunciator.chats_read().keys():
                Annunciator.add_to_chatlist(Annunciator.chats_read(), self.bot.peer_id, self.validator.get_groupname())
                self.bot.send_message(f"Чат с ID:{self.bot.peer_id} || Группа:{self.validator.get_groupname()} успешно добавлен в систему оповещений!")
            else:
                self.bot.send_message("Данный чат уже находится в системе оповещений.")
        else:
            self.bot.send_message("Отсутствует номер группы.")

    @loggit
    def remove_from_annons(self):
        """Удаляет чат из системы оповещений"""
        if str(self.bot.peer_id) in Annunciator.chats_read().keys():
            Annunciator.remove_from_chatlist(Annunciator.chats_read(), self.bot.peer_id)
            self.bot.send_message(f"Чат с ID:{self.bot.peer_id} удалён из системы оповещений.")
        else:
            self.bot.send_message("Данный чат не находится в системе оповещений.")

    def debug_checkid(self):
        """Админ-команда для просмотра chat id"""
        #     self.bot.send_message(self.bot.peer_id)
        pass

    def debug_manualstart(self):
        """Админ-команда для ручного запуска системы оповещений"""
        #if self.bot.peer_id == 406579945:
        # manual = Annunciator(self.bot)
        pass

