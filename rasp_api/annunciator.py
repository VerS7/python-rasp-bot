import json
import time
from rasp_api import Schedule, Util, vkUtils


class Annunciator:
    def __init__(self, bot_handler: vkUtils.BotHandler):
        self.bh = bot_handler
        self.chats = Annunciator.chats_read()

    @staticmethod
    def add_to_chatlist(chat_list, chat_id, groupname):
        """Adds chat_id to announce base in json"""
        with open("chats_list.json", 'w', encoding='utf-8') as chats:
            chat_list[chat_id] = groupname
            json.dump(chat_list, chats)

    @staticmethod
    def chats_read():
        """Returns data from chat_list json"""
        with open("chats_list.json", 'r', encoding='utf-8') as chats:
            chats = json.load(chats)
            return chats

    def send_daily(self, chat_id, groupname):
        """Send daily schedules"""
        img = Util.pilobj_to_bytes(Schedule.reading_img(groupname, "raspback.png"))
        self.bh.peer_id = chat_id
        self.bh.send_image(img, f"Оповещение расписания для группы {groupname}")

    def run(self):
        """Run announce system in timing"""
        self.chats = Annunciator.chats_read()
        for elem in self.chats:
            try:
                self.send_daily(elem, self.chats.get(elem))
            except Exception as e:
                print(f'Something went wrong in announciator itering group: {elem}, chat_id: {self.chats.get(elem)}', e)
                continue
