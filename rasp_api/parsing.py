"""
Парсинг данных с сайта расписания.
"""
import re
from typing import Tuple, List, Dict
from asyncio import new_event_loop, get_event_loop, AbstractEventLoop

from aiohttp import ClientSession
from aiohttp.web import HTTPException

from bs4 import BeautifulSoup
from bs4.element import Tag

URL_DAILY = "http://dmitrov-dubna.ru/shedule/hg.htm"
URL_WEEKLY = "http://dmitrov-dubna.ru/shedule/cg.htm"
URL_MAINLY = "http://dmitrov-dubna.ru/shedule/bg.htm"
URL_RESULTS = "http://dmitrov-dubna.ru/shedule/vg.htm"
URL_TEACHER = "http://dmitrov-dubna.ru/shedule/vp.htm"

PARSER = "html.parser"


class Parser:
    """
    Базовый парсер
    """
    def __init__(self, loop: AbstractEventLoop | None, session: ClientSession | None = None):
        if not loop:
            if get_event_loop() is None:
                self.loop = new_event_loop()
            else:
                self.loop = get_event_loop()
        else:
            self.loop = loop

        if not session:
            self.session = ClientSession(loop=self.loop)
        else:
            self.session = session

    async def parse_request(self, url: str) -> BeautifulSoup:
        """
        Парсит страницу по ссылке
        :param str url: url страницы
        """
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(text="Сайт не отвечает.")

            return BeautifulSoup(await response.read(), features=PARSER)

    def get_update(self, soup: BeautifulSoup) -> str:
        """
        Возвращает строку состояния последнего обновления расписания
        :param BeautifulSoup soup: распарсеный HTML
        """
        return soup.find('.ref').get_text()

    def get_day(self, soup: BeautifulSoup) -> str:
        """
        Возвращает строку текущего дня
        :param BeautifulSoup soup: распарсеный HTML
        """
        return soup.find('.zgr').get_text()

    def get_exact_update(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """
        Возвращает конкретное значение даты и времени обновления
        :param BeautifulSoup soup: распарсеный HTML
        """
        match = re.search(r"(\d{2}\.\d{2}\.\d{4})\sв\s(\d{2}:\d{2})", self.get_update(soup))
        if match:
            return match.group(1), match.group(2)

    def _process_raw_schedule(self, raw: List[Tag]) -> Tuple[str, List[Tuple[str, Tuple[str | None] | None]]]:
        schedule_header = raw[0].get_text(separator=" ")
        headers = []
        contents = []

        for elem in raw[1::]:
            if elem.attrs["class"][0] == "hd":
                headers.append(elem.get_text(separator=" ").replace("\n", ""))

            if elem.attrs["class"][0] == "ur":
                z1, z2, z3 = (elem.find("a", class_="z1"),
                              elem.find("a", class_="z2"),
                              elem.find("a", class_="z3"))

                contents.append((z1.get_text() if z1 else None,
                                 z2.get_text() if z2 else None,
                                 z3.get_text() if z3 else None))

            if elem.attrs["class"][0] == "nul":
                contents.append(None)

        return schedule_header, list(zip(headers, contents))


class TagsParser(Parser):
    """
    Парсинг тэгов и названий групп
    """
    def __init__(self, loop: AbstractEventLoop | None = None, session: ClientSession | None = None):
        super().__init__(loop, session)
        self._soup = None
        self._tags: Dict[str, str] = {}

    async def parse_tags(self, soup: BeautifulSoup | None = None, force=False) -> Dict[str, str]:
        """
        Парсит название групп и тэгов
        :param BeautifulSoup soup: распарсеный HTML
        :param bool force: получить тэги по новой если они уже существуют
        """
        if soup:
            self._soup = soup

        if force or not self._tags:
            self._soup = await self.parse_request(URL_WEEKLY)

            for a in self._soup.find("table", {"class": "inf"}).find_all("a", {"class": "z0"}):
                self._tags[a.get_text()] = re.search(r"(?<=\D)\d+", a.attrs["href"]).group()

            return self._tags

        if self._tags:
            return self._tags

    async def validate(self, groupname: str) -> Tuple[str, str] | None:
        """
        Возвращает Tuple с названием группы и тэгом по первому совпадению groupname
        :param str groupname:
        """
        if not self._tags:
            await self.parse_tags()

        for k, v in self._tags.items():
            if groupname in k:
                return k, v


class DailyParser(Parser):
    """
    Парсинг ежедневного расписания по всем группам
    """
    def __init__(self, loop: AbstractEventLoop | None = None, session: ClientSession | None = None):
        super().__init__(loop, session)
        self._soup = None

    async def get_all_daily(self) -> Dict[str, List[Tuple[str, Tuple[str | None] | None]]]:
        """Возвращает текущее дневное расписание для всех групп."""
        if not self._soup:
            self._soup = await self.parse_request(URL_DAILY)

        groups = {}
        current = []

        for td in self._soup.find("table", {"class": "inf"}).find_all("td")[4::]:
            if td.attrs["class"][0] == "hd0":  # Разделитель групп
                group, schedule = self._process_raw_schedule(current)
                groups[group] = schedule
                current = []
                continue

            current.append(td)

        return groups

    async def get_daily(self, groupname: str) -> List[Tuple[str, Tuple[str | None] | None]]:
        """
        Возвращает список расписания на день по имени группы или None
        :param str groupname: номер/название группы
        """
        all_daily = await self.get_all_daily()
        return all_daily.get(groupname)

    async def get_update(self, soup: BeautifulSoup | None = None) -> str:
        """
        Возвращает строку состояния последнего обновления расписания
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(URL_DAILY)

        return super().get_update(self._soup)

    async def get_day(self, soup: BeautifulSoup | None = None) -> str:
        """
        Возвращает строку текущего дня
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(URL_DAILY)

        return super().get_day(self._soup)

    async def get_exact_update(self, soup: BeautifulSoup | None = None) -> Tuple[str, str]:
        """
        Возвращает конкретное значение даты и времени обновления
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(URL_DAILY)

        return super().get_exact_update(self._soup)


class WeekParser(Parser):
    """
    Парсинг недельного расписания конкретной группы
    """
    def __init__(self, grouptag: str, loop: AbstractEventLoop | None = None, session: ClientSession | None = None):
        super().__init__(loop, session)
        self._url = URL_WEEKLY.replace("cg", f"cg{grouptag}")
        self._soup = None

    async def get_update(self, soup: BeautifulSoup | None = None) -> str:
        """
        Возвращает строку состояния последнего обновления расписания
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(self._url)

        return super().get_update(self._soup)

    async def get_exact_update(self, soup: BeautifulSoup | None = None) -> Tuple[str, str]:
        """
        Возвращает конкретное значение даты и времени обновления
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(self._url)

        return super().get_exact_update(self._soup)

    async def get_week(self,
                       soup: BeautifulSoup | None = None
                       ) -> Dict[str, List[Tuple[str, Tuple[str | None] | None]]]:
        """
        Возвращает недельное расписание.
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(self._url)

        days = {}
        current = []

        for td in self._soup.find("table", {"class": "inf"}).find_all("td")[8::]:
            if td.attrs["class"][0] == "hd0":  # Разделитель групп
                if len(current) == 0:  # Пропуск в случае если не набралось расписание
                    continue
                day, schedule = self._process_raw_schedule(current)
                days[day] = schedule
                current = []
                continue

            if td.attrs["class"][0] == "hd" and td.get_text() in ("День", "Неделя 1", "Неделя 2", "Пара"):
                # Пропуск td, в котором находится структурная информация
                continue

            current.append(td)

        return days


class MainParser(WeekParser):
    """
    Парсинг основного расписания конкретной группы
    """
    def __init__(self, grouptag: str, loop: AbstractEventLoop | None = None, session: ClientSession | None = None):
        super().__init__(grouptag, loop, session)
        self._url = URL_MAINLY.replace("bg", f"bg{grouptag}")

    async def get_main(self,
                       soup: BeautifulSoup | None = None
                       ) -> Dict[str, List[Tuple[str, Tuple[str | None] | None]]]:
        """
        Возвращает основное расписание.
        :param BeautifulSoup soup: распарсеный HTML
        """
        if soup:
            self._soup = soup

        if not self._soup:
            self._soup = await self.parse_request(self._url)

        return await self.get_week(self._soup)


class TeachersParser(Parser):
    def __init__(self, loop: AbstractEventLoop | None, session: ClientSession | None = None):
        super().__init__(loop, session)

    def get_all_teachers(self, soup: BeautifulSoup) -> list:
        raise NotImplementedError

    def get_daily_teacher(self, teacher: str, soup: BeautifulSoup) -> list:
        """
        :param str teacher: Фамилия/Имя препода
        """
        raise NotImplementedError
