# -*- coding: utf-8 -*-
"""
Парсинг данных с сайта расписания.
"""
import re
from typing import Tuple, List

import requests
from bs4 import BeautifulSoup


URL_DAILY = "http://dmitrov-dubna.ru/shedule/hg.htm"
URL_WEEKLY = "http://dmitrov-dubna.ru/shedule/cg.htm"
URL_MAINLY = "http://dmitrov-dubna.ru/shedule/bg.htm"
URL_RESULTS = "http://dmitrov-dubna.ru/shedule/vg.htm"
URL_TEACHER = "http://dmitrov-dubna.ru/shedule/vp.htm"


def parse_request(url: str) -> "BeautifulSoup":
    """
    Парсит страницу по ссылке
    :param str url: url-ссылка на страницу
    """
    try:
        api = requests.get(url)
    except Exception as e:
        raise e
    if api.status_code != 200:
        raise requests.RequestException("Сайт не отвечает.")
    return BeautifulSoup(api.text, 'html.parser')


def get_all_daily(soup: BeautifulSoup) -> dict:
    """Возвращает текущее дневное расписание для всех групп."""
    groups = {}
    current = []
    for elem in soup.select('.inf'):
        if len(elem) < 100:
            raise Exception("Ошибка в получении данных с сайта.")
        for row in list(elem)[4:]:
            if row.get_text() == '\n':
                if current:
                    if '\n' in current:
                        current.remove('\n')
                    group_name = current[0][0]
                    del current[0][0]
                    groups[group_name] = current
                current = [row]
            elif len(row.get_text()) > 1:
                current.append(row.get_text(strip=True, separator="|")
                                  .encode('latin1')
                                  .decode('cp1251')
                                  .split("|"))
    return groups


def get_group_week(grouptag: str) -> Tuple[str, str, List[dict]]:
    """
    Возвращает недельное расписание для конкретной группы по groupname
    :param str grouptag: тэг конкретной группы
    :return: группа, обновление, недельное расписание
    """
    return __get_week_or_main(parse_request(URL_WEEKLY.replace("cg", f"cg{grouptag}")))


def get_group_main(grouptag: str) -> Tuple[str, str, List[dict]]:
    """
    Возвращает основное расписание для конкретной группы по groupname
    :param str grouptag: номер/название группы
    :return: группа, обновление, основное расписание
    """
    return __get_week_or_main(parse_request(URL_WEEKLY.replace("bg", f"bg{grouptag}")))


def __get_week_or_main(soup: BeautifulSoup) -> Tuple[str, str, List[dict]]:
    week = []
    temp = []
    group = soup.find("div").find('h1').get_text().encode('latin1').decode('cp1251').split()[1]
    for elem in soup.select('.inf'):
        for row in list(elem)[5:]:
            if "\n" in row:
                if "День" not in temp[0]:  # Проверка на День Пара Неделя 2. Костыль :/
                    if len(temp[0][0]) > 9:  # Проверка на полную дату. Костыль :/
                        day = f"{temp[0][0]}  {temp[0][1]}"
                        del temp[0][0]  # Удаление полной даты
                        del temp[0][0]  # Удаление дня недели
                    else:
                        day = temp[0][0]
                        del temp[0][0]
                    week.append({day: temp.copy()})
                temp.clear()
            else:
                text = row.get_text(strip=True, separator="|")\
                          .encode('latin1')\
                          .decode('cp1251')\
                          .split("|")

                if not len(text) == 1:
                    temp.append(text)

    return group, get_update(), week


def get_daily(groupname: str, soup: BeautifulSoup = None) -> list:
    """
    Возвращает list расписания на день по имени группы или None
    :param str groupname: номер/название группы
    """
    if soup:
        parsed = soup
    else:
        parsed = parse_request(URL_DAILY)

    return get_all_daily(parsed).get(groupname)


def get_update(soup: BeautifulSoup = None) -> str:
    """Возвращает строку состояния последнего обновления расписания"""
    if soup:
        parsed = soup
    else:
        parsed = parse_request(URL_DAILY)

    data = parsed.select('.ref')
    update = data[0].get_text().encode('latin1').decode('cp1251').strip("\r\n")
    return update


def get_day(soup: BeautifulSoup = None) -> str:
    """Возвращает строку текущего дня"""
    if soup:
        parsed = soup
    else:
        parsed = parse_request(URL_DAILY)

    soup = parsed.select('.zgr')
    day = soup[0].get_text().encode('latin1').decode('cp1251').strip("\r\n")
    if len(day) > 10:
        return day
    raise Exception("Не удалось получить текущий день.")


def get_exact_update(soup: BeautifulSoup = None) -> tuple:
    """Возвращает конкретное значение даты и времени обновления"""
    if soup:
        parsed = soup
    else:
        parsed = parse_request(URL_DAILY)

    match = re.search(r"(\d{2}\.\d{2}\.\d{4})\sв\s(\d{2}:\d{2})", get_update(parsed))
    if match:
        return match.group(1), match.group(2)
    raise Exception("Не удалось получить дату и время.")


def get_all_teachers(soup: BeautifulSoup) -> list:
    raise NotImplementedError


def get_daily_teacher(teacher: str, soup: BeautifulSoup) -> list:
    """
    :param str teacher: Фамилия/Имя препода.
    """
    raise NotImplementedError
