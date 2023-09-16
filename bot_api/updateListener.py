import time
import requests
from bs4 import BeautifulSoup


class UpdateListener:
    def __init__(self, delay=3600):
        """Delay по умолчанию равен 30 минутам."""
        self.delay = delay
        self.update = self.updater()

    def updater(self):
        """Проверяет обновление на сайте."""
        try:
            api = requests.get("http://shedule.uni-dmitrov.ru/hg.htm")
            content = api.text
            soup = BeautifulSoup(content, 'html.parser')
            soup = soup.select('.ref')
            update = (soup[0].get_text(strip=True, separator='|').encode('latin1').decode('cp1251'))
            return update
        except Exception as e:
            print(e)

    def run(self):
        while True:
            """Цикл проверки обновления на сайте."""
            if self.update != self.updater():
                self.update = self.updater()
                print(self.update, 'Обновилось!')
            else:
                print('no update!')
            time.sleep(self.delay)
