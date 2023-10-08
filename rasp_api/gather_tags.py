# -*- coding: utf-8 -*-
"""
Работа с тэгами и номерами групп.
"""
from typing import Union
from .Parsing import parse_request


def get_tags(url: str) -> dict:
    """
    Возращает dict названий групп и тэгов
    :param str url: url, откуда берутся raw тэги
    """
    tagnames = {}
    soup = parse_request(url)
    for link in soup.find_all("a", {'class': 'z0'}):
        href = link["href"].split("cg")[1].split(".")[0]
        title = link.get_text().encode('latin1').decode('cp1251')
        tagnames[title] = href
    return tagnames


def validate_groupname(groupname: str, tags: dict) -> Union[str, None]:
    """
    Возвращает первый валидный номер группы по неполному номеру группы или None
    :param str groupname: номер/название группы
    :param dict tags: тэги всех групп
    """
    for elem in tags.keys():
        if groupname in elem:
            return elem
    return None


def tag_search(groupname: str, tags: dict) -> Union[str, None]:
    """
    Возвращает первый найденный тэг по номеру группы или None
    :param str groupname: номер/название группы
    :param dict tags: тэги всех групп
    """
    if len(tags) < 1:
        raise Exception("Не удалось получить tag dict.")
    for i in tags:
        if groupname in i:
            return tags.get(i)
    return None
