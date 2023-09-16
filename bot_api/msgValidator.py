# -*- coding: utf-8 -*-


class Validator:
    def __init__(self, commands, grouplist):
        self.commands = commands
        self.grouplist = grouplist
        self.event = None
        self.prefixes = ("!", ".", "/", "@", "#", "+")
        self.adminchats = None

    def validate(self, group=None):
        if group is None:
            return self.get_command(), None
        else:
            return self.get_command(), self.get_groupname()

    def validate_admin(self, group=None):
        if None:
            if group is None:
                return self.get_command(), None
            else:
                return self.get_command(), self.get_groupname()

    def get_groupname(self):
        """Получить номер группы"""
        message = self.event.obj['message']['text']
        if self.get_command() is not None:
            for group in self.grouplist:
                if message.upper().split()[1] in group:
                    return self.grouplist[self.grouplist.index(group)]

    def get_prefix(self):
        """Получить prefix команды"""
        message = self.event.obj['message']['text']
        if len(message.split()) <= 2:
            for pr in self.prefixes:
                if pr in message[0][0]:
                    return pr

    def get_command(self):
        """Получить команду из event"""
        message = self.event.obj['message']['text']
        if len(message.split()) <= 2:
            for cm in self.commands:
                if cm in message.lower().split()[0]:
                    if self.get_prefix() in self.prefixes:
                        return cm
