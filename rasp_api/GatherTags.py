# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup


class GatherTags:
    """Функции обработки названий групп/тэгов"""

    @staticmethod
    def tagsparse() -> tuple:
        """Получение названий групп и тэгов"""
        try:
            url = "http://dmitrov-dubna.ru/shedule/cg.htm"
            api = requests.get(url)
            content = api.text
            soup = BeautifulSoup(content, 'html.parser')
            groupnames = []
            grouptags = []
            for i in soup.findAll('a', {'class': 'z0'}):
                groupnames.append(i.getText().encode('latin1').decode('cp1251'))
            for i in soup.findAll('a'):
                tag = i.get('href')
                if type(tag) is str and len(tag) == 9:
                    grouptags.append(tag)
            del grouptags[0]
            return grouptags, groupnames
        except Exception as e:
            raise e

    @staticmethod
    def tagsprettify() -> dict:
        """Создание словаря Группа:Тэг"""
        try:
            x, z = GatherTags.tagsparse()
            y = []
            m = []
            final = {}
            for i in x:
                y.append(re.findall(r'\d+', i))
            for i in z:
                m.append(re.sub(r'(\(о\))', '', i))
            for i in range(len(y)):
                final[m[i]] = "".join(y[i])
            return final
        except Exception as e:
            print(e)

    @staticmethod
    def tagsearch(groupname: str, tags: dict):
        """Возвращает первый найденный тэг по номеру группы"""
        try:
            for i in tags:
                if groupname in i:
                    return tags.get(i)
        except Exception as e:
            print(e)

    @staticmethod
    def grouplist_create() -> list:
        """Создаёт список групп"""
        final = []
        for i in GatherTags.tagsprettify():
            final.append(i)
        return final

    @staticmethod
    def groupname_validation(groupname: str, grouplist: list):
        """Проверяет наличие группы в списке групп"""
        try:
            for i in grouplist:
                if groupname.upper() in i:
                    return True
            return False
        except Exception as e:
            print(e)
            return False
