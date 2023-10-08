# -*- coding: utf-8 -*-
"""
Создание изображений с расписанием.
"""
from os import path
from typing import Union

from .parsing import *
from PIL import Image, ImageDraw, ImageFont


IMAGE_SIZE = (1200, 1500)
MAIN_IMAGE_FONT = ImageFont.truetype("impact.ttf", size=35)
OTHER_IMAGE_FONT = ImageFont.truetype("impact.ttf", size=50)
BG_IMAGE = path.join(path.dirname(path.abspath(__file__)), "../files/raspback.png")


def __prettify_for_image(schedule: list) -> list:
    """
    Возвращает подготовленный для изображения список строк
    :param list schedule: список расписания конкретной группы
    """
    result = []
    for elem in schedule:
        result.append(" ".join(elem[0:2]))
        if len(elem) > 2:
            result.append("\n".join([__prettify_length(line) for line in elem[2::]]))
        else:
            pass
        result.append("-" * 90)
    return result


def __prettify_length(string: str) -> str:
    """
    Укорачивает длинные строки
    :param string: Строка
    :return: Изначальная или укороченная строка
    """
    if len(string) > 55:
        if len(" ".join(string.split()[0:5])) > 55:
            return " ".join(string.split()[0:4]) + "..."
        return " ".join(string.split()[0:5]) + "..."
    return string


def daily_image(groupname: str, resize_multiplier: Union[None, float] = None) -> Image.Image:
    """
    Расписание на день в PIL Image object
    :param str groupname: название/номер группы
    :param resize_multiplier: Множитель размера изображения.
    1 = default, 0.5 - изображение в 2 раза меньше
    """
    background = Image.open(BG_IMAGE)
    rasp_image = ImageDraw.Draw(background)

    update = get_update()
    time = get_day()
    daily = __prettify_for_image(get_daily(groupname))

    rasp_image.text((460, 100), time, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((510, 160), groupname, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((120, 240), "\n".join(daily), font=MAIN_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((290, 1300), update, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))

    if resize_multiplier:
        return background.resize((int(IMAGE_SIZE[0] * resize_multiplier),
                                  int(IMAGE_SIZE[1] * resize_multiplier)))
    return background.resize(IMAGE_SIZE)


def __create_images(grouptag: str,
                    rasp_type: str,
                    resize_multiplier:
                    Union[None, float] = None) -> List[Image.Image]:
    """
    Создаёт список недельного/основого расписания в PIL Image objects
    :param str grouptag: тэг группы
    :param str rasp_type: тип расписания. week - недельное, main - основное
    :param resize_multiplier: Множитель размера изображения. 
    1 = default, 0.5 - изображение в 2 раза меньше
    :return: Список с PIL объектами изображений недельного расписания
    """
    rasp = []
    result = []
    size = IMAGE_SIZE

    if rasp_type == "week":
        rasp = get_group_week(grouptag)
    if rasp_type == "main":
        rasp = get_group_main(grouptag)

    if resize_multiplier:
        size = (int(IMAGE_SIZE[0] * resize_multiplier), int(IMAGE_SIZE[1] * resize_multiplier))

    group: str = rasp[0]
    update: str = rasp[1]
    schedule: List[dict] = rasp[2]

    for day in schedule:
        background = Image.open(BG_IMAGE)
        rasp_image = ImageDraw.Draw(background)
        prettified = __prettify_for_image(list(*day.values()))

        date = str(*list(day.keys()))
        date_xy = (550, 100)
        if len(date) > 8:
            date_xy = (460, 100)

        rasp_image.text(date_xy, date, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
        rasp_image.text((510, 160), group, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
        rasp_image.text((120, 240), "\n".join(prettified), font=MAIN_IMAGE_FONT, fill=(86, 131, 172))
        rasp_image.text((290, 1300), update, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))

        result.append(background.resize(size))

    return result


def weekly_images(grouptag: str, resize_multiplier: Union[None, float] = None) -> List[Image.Image]:
    """
    Создаёт список недельного расписания в PIL Image objects
    :param str grouptag: тэг группы
    :param resize_multiplier: Множитель размера изображения.
    1 = default, 0.5 - изображение в 2 раза меньше
    :return: Список с PIL объектами изображений недельного расписания
    """
    return __create_images(grouptag, "week", resize_multiplier)[0:7]


def mainly_images(grouptag: str, resize_multiplier: Union[None, float] = None) -> List[Image.Image]:
    """
    Создаёт список основого расписания в PIL Image objects
    :param str grouptag: тэг группы
    :param resize_multiplier: Множитель размера изображения.
    1 = default, 0.5 - изображение в 2 раза меньше
    :return: Список с PIL объектами изображений недельного расписания
    """
    return __create_images(grouptag, "week", resize_multiplier)
