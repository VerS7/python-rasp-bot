# -*- coding: utf-8 -*-
import re
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import Tuple


URL_DAILY = "http://dmitrov-dubna.ru/shedule/hg.htm"
URL_WEEKLY = "http://dmitrov-dubna.ru/shedule/cg.htm"
URL_MAINLY = "http://dmitrov-dubna.ru/shedule/bg.htm"
URL_RESULTS = "http://dmitrov-dubna.ru/shedule/vg.htm"
URL_TEACHER = "http://dmitrov-dubna.ru/shedule/vp.htm"


async def parse_request(url: str) -> "BeautifulSoup":
    """
    Парсит страницу по ссылке
    :param str url: url-ссылка на стриницу
    """
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Не удалось получить данные. Статус: {response.status}")
            return BeautifulSoup(await response.text(), 'html.parser')


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
                current.append(row.get_text(strip=True, separator="|").encode('latin1').decode('cp1251').split("|"))
    return groups


def get_group_weekly(grouptag: str) -> Tuple[str, str, list]:
    """
    Возвращает недельное расписание для конкретной группы по groupname
    :param str grouptag: тэг конкретной группы
    :return: группа, обновление, недельное расписание
    """
    return __get_week_or_main(parse_request(URL_WEEKLY.replace("cg", f"bg{grouptag}")))


def get_group_main(grouptag: str) -> Tuple[str, str, list]:
    """
    Возвращает основное расписание для конкретной группы по groupname
    :param str grouptag: номер/название группы
    :return: группа, обновление, основное расписание
    """
    return __get_week_or_main(parse_request(URL_WEEKLY.replace("cg", f"cg{grouptag}")))


def __get_week_or_main(soup: BeautifulSoup) -> Tuple[str, str, list]:
    week = []
    temp = []
    group = soup.find("div").find('h1').get_text().encode('latin1').decode('cp1251').split()[1]
    for elem in soup.select('.inf'):
        for row in list(elem)[5:]:
            if "\n" in row:
                week.append(temp.copy())
                temp.clear()
            else:
                text = row.get_text(strip=True, separator="|").encode('latin1').decode('cp1251').split("|")
                if not len(text) == 1:
                    temp.append(text)
    return group, get_update(), week


def get_daily(groupname: str):
    """
    Возвращает list расписания на день по имени группы или None
    :param str groupname: номер/название группы
    """
    return get_all_daily(parse_request(URL_DAILY)).get(groupname)


def get_update() -> str:
    """Возвращает строку состояния последнего обновления расписания"""
    soup = parse_request(URL_DAILY).select('.ref')
    update = soup[0].get_text().encode('latin1').decode('cp1251').strip("\r\n")
    return update


def get_day() -> str:
    """Возвращает строку текущего дня"""
    soup = parse_request(URL_DAILY).select('.zgr')
    day = soup[0].get_text().encode('latin1').decode('cp1251').strip("\r\n")
    if len(day) > 10:
        return day
    raise Exception("Не удалось получить текущий день.")


def get_exact_update() -> tuple:
    """Возвращает конкретное значение даты и времени обновления"""
    match = re.search(r"(\d{2}\.\d{2}\.\d{4})\sв\s(\d{2}:\d{2})", get_update())
    if match:
        return match.group(1), match.group(2)
    raise Exception("Не удалось получить дату и время.")


def get_all_teachers(soup: BeautifulSoup) -> list:
    raise "Не определено. На будущее"


def get_daily_teacher(teacher: str, soup: BeautifulSoup) -> list:
    raise "Не определено. На будущее"
