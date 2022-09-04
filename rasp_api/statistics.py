import csv
import time


class Statistics:
    def __init__(self, filepath):
        self.fp = filepath
        self.fieldnames = ('chat_id', 'command', 'time')

    def stat_read(self):
        """Считывает статистику с csv file"""
        with open(self.fp, 'r', encoding='unicode_escape') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=self.fieldnames)
            data_read = [row for row in reader]
            print(data_read)

    def stat_add(self, statdict):
        """Записывает статистику в csv file"""
        with open('statistics.csv', 'a', encoding='unicode_escape') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(statdict)


class StatisticsHandler(Statistics):
    def __init__(self, filepath):
        super().__init__(filepath)

    @classmethod
    def to_dict(cls, event):
        """Создаёт dict object из vk event"""
        chat_id = event.obj['message']['peer_id']
        message = event.obj['message']['text'].split()[0]
        cur_time = time.ctime(time.time())
        return {'chat_id': chat_id, 'command': message, 'time': cur_time}

    def write_stats(self, event):
        """Записывает статистику в csv file"""
        self.stat_add(self.to_dict(event))
