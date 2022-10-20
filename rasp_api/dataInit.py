# -*- coding: utf-8 -*-
import configparser
from dataclasses import dataclass
from rasp_api.GatherTags import *
from rasp_api.statistics import StatisticsHandler


@dataclass
class DataInit:
    """Конфиги"""
    def __init__(self, config, statfile, infofile, commandsfile):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config)
        """Размер изображения расписания"""
        self.size = int(self.cfg['image']['width']), int(self.cfg['image']['length'])
        """Статистика"""
        self.stats = StatisticsHandler(statfile)
        """Токен и ID сообщества"""
        self.token = self.cfg['bot']['token']
        self.id = self.cfg['bot']['pubid']
        """Тэги"""
        self.tags = GatherTags.tagsprettify()
        """Группы"""
        self.grouplist = GatherTags.grouplist_create()
        """Инфо"""
        with open(infofile, "r", encoding="utf-8") as info:
            self.info = info.read()
        """Команды"""
        with open(commandsfile, "r", encoding="utf-8") as comlist:
            self.comlist = [row.strip() for row in comlist]
