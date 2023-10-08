# -*- coding: utf-8 -*-
"""
Валидация номера группы.
"""
from typing import Union
from .gather_tags import get_tags
from .parsing import URL_WEEKLY


GROUPTAGS = get_tags(URL_WEEKLY)


def get_tag(groupname: str) -> Union[str, None]:
    """
    :param str groupname: имя группы
    :return: тэг группы или None
    """
    __groupname = validate_groupname(groupname)
    if __groupname:
        return GROUPTAGS[__groupname]
    return None


def validate_groupname(groupname: str) -> Union[str, None]:
    """
    :param str groupname: имя группы
    :return: конкретное имя группы или None
    """
    for elem in GROUPTAGS.keys():
        if groupname in elem:
            return elem
    return None
