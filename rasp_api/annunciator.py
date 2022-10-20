# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from rasp_api import Schedule, Util, vkUtils
from rasp_api.simplelogger import loggit


class Annunciator:
    """Система оповещений по таймингам"""
    def __init__(self, bot_handler: vkUtils.BotHandler, delay=1):
        self.bh = bot_handler
        self.chats = Annunciator.chats_read()
        self.timings = ['19:00', "05:00", "00:00"]
        self.delay = delay

    @staticmethod
    def add_to_chatlist(chat_list: dict, chat_id: int, groupname: str):
        """Добавляет chat_id в базу оповещений json"""
        with open("chats_list.json", 'w', encoding='utf-8') as chats:
            chat_list[chat_id] = groupname
            json.dump(chat_list, chats)

    @staticmethod
    def chats_read():
        """Возвращает данные из файла chats_list"""
        with open("chats_list.json", 'r', encoding='utf-8') as chats:
            chats = json.load(chats)
            return chats

    @loggit
    def send_daily(self, chat_id: int, groupname: str):
        """Отправляет оповещение по chat_id и groupname"""
        img = Util.pilobj_to_bytes(Schedule.reading_img(groupname, "raspback.png"))
        self.bh.peer_id = chat_id
        self.bh.send_image(img, f"Оповещение расписания для группы {groupname}")

    def chats_send(self):
        self.chats = Annunciator.chats_read()
        for elem in self.chats:
            try:
                self.send_daily(elem, self.chats.get(elem))
            except Exception as e:
                print(f'---Проблема в итерации оповещений: {elem}, chat_id: {self.chats.get(elem)}', e)
                continue

    def run(self):
        """Запуск системы оповещений"""
        run = True
        while run:
            current_time = datetime.now().strftime("%H:%M")
            time.sleep(self.delay)
            if current_time in self.timings:
                self.chats_send()
                """Переключатель оповещения"""
                run = False
                time.sleep(60)
                run = True
