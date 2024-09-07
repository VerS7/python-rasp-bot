"""
Создание изображений с расписанием
"""
from os import path
from typing import List, Dict, Tuple

from .parsing import TagsParser, DailyParser, WeekParser, MainParser
from PIL import Image, ImageDraw, ImageFont

IMAGE_SIZE = (1200, 1500)
FONT_PATH = path.join(path.dirname(path.dirname(path.abspath(__file__))), "files/impact.ttf")
MAIN_IMAGE_FONT = ImageFont.truetype(FONT_PATH, size=35)
OTHER_IMAGE_FONT = ImageFont.truetype(FONT_PATH, size=50)
BG_IMAGE = path.join(path.dirname(path.dirname(path.abspath(__file__))), "files/raspback.png")


def _prettify_for_image(schedule: list) -> list:
    """
    Возвращает подготовленный для изображения список строк
    :param list schedule: список расписания конкретной группы
    """
    result = []
    for elem in schedule:
        result.append(elem[0])

        if elem[1]:
            result.append(_prettify_length(elem[1][0]))
            result.append(elem[1][1]) if elem[1][1] else None
            result.append(elem[1][2]) if elem[1][2] else None

        result.append("-" * 90)

    return result


def _prettify_length(string: str) -> str:
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


class ScheduleImageGenerator:
    def __init__(self, resize_multiplier: float | None = None):
        self.resize_multiplier = resize_multiplier
        self._tagsparser = TagsParser()

    async def create_daily(self, groupname: str) -> Image.Image:
        """
        Создаёт расписание на день по номеру группы
        :param str groupname: номер группы
        """
        group = await self._tagsparser.validate(groupname)
        if not group:
            raise ValueError(f"Нет совпадений групп с названием {group}")

        background = Image.open(BG_IMAGE)
        image = ImageDraw.Draw(background)

        daily = DailyParser()
        update = await daily.get_update()
        day = await daily.get_day()
        schedule = _prettify_for_image(await daily.get_daily(group[0]))
        await daily.session.close()

        image.text((460, 100), day, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
        image.text((510, 160), group[0], font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
        image.text((120, 240), "\n".join(schedule), font=MAIN_IMAGE_FONT, fill=(86, 131, 172))
        image.text((290, 1300), update, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))

        if self.resize_multiplier:
            return background.resize((int(IMAGE_SIZE[0] * self.resize_multiplier),
                                      int(IMAGE_SIZE[1] * self.resize_multiplier)))

        return background.resize(IMAGE_SIZE)

    async def create_week(self, groupname: str) -> List[Image.Image]:
        """
        Создаёт список недельного расписания по номеру группы
        :param str groupname: номер группы
        """
        group = await self._tagsparser.validate(groupname)
        if not group:
            raise ValueError(f"Нет совпадений групп с названием {group}")

        parser = WeekParser(group[1])
        update, week = await parser.get_update(), await parser.get_week()
        await parser.session.close()

        return self.__create_images(group[0], update, week)

    async def create_main(self, groupname: str) -> List[Image.Image]:
        """
        Создаёт список основного расписания по номеру группы
        :param str groupname: номер группы
        """
        group = await self._tagsparser.validate(groupname)
        if not group:
            raise ValueError(f"Нет совпадений групп с названием {group}")

        parser = MainParser(group[1])
        update, week = await parser.get_update(), await parser.get_week()
        await parser.session.close()

        return self.__create_images(group[0], update, week)

    def __create_images(self,
                        groupname: str,
                        update: str,
                        schedule: Dict[str, List[Tuple[str, Tuple[str | None] | None]]]
                        ) -> List[Image.Image]:
        result = []

        size = IMAGE_SIZE
        if self.resize_multiplier:
            size = (int(IMAGE_SIZE[0] * self.resize_multiplier), int(IMAGE_SIZE[1] * self.resize_multiplier))

        for day, elem in schedule.items():
            background = Image.open(BG_IMAGE)
            rasp_image = ImageDraw.Draw(background)
            prettified = _prettify_for_image(elem)

            day_xy = (550, 100)
            if len(day) > 8:
                day_xy = (460, 100)

            rasp_image.text(day_xy, day, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
            rasp_image.text((510, 160), groupname, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
            rasp_image.text((120, 240), "\n".join(prettified), font=MAIN_IMAGE_FONT, fill=(86, 131, 172))
            rasp_image.text((290, 1300), update, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))

            result.append(background.resize(size))

        return result
