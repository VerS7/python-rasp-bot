"""
Тесты модуля парсинга
"""

from unittest import IsolatedAsyncioTestCase, main

from rasp_api.parsing import *


class TestTagsParser(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.parser = TagsParser()

    async def asyncTearDown(self):
        await self.parser.session.close()

    async def test_get_tags(self):
        tags = await self.parser.parse_tags()
        self.assertIsInstance(tags, dict)
        self.assertGreater(len(tags), 0)

    async def test_get_validated(self):
        self.assertEqual(await self.parser.validate("0121"), ("0121-АС", "544"))


class TestDailyParser(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.parser = DailyParser()

    async def asyncTearDown(self):
        await self.parser.session.close()

    async def test_get_daily(self):
        d = await self.parser.get_daily("0121-АС")
        self.assertIsInstance(d, list)
        self.assertGreater(len(d), 0)
        for e in d:
            self.assertIsInstance(e, tuple)
            self.assertIsInstance(e[0], str)
            self.assertIsInstance(e[1], tuple | None)

    async def test_get_wrong_daily(self):
        d = await self.parser.get_daily("...")
        self.assertIsNone(d)

    async def test_get_all_daily(self):
        d = await self.parser.get_all_daily()
        items = d.items()
        self.assertIsInstance(d, dict)
        for k, v in items:
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, list)
        self.assertIsInstance(list(items)[0][1], list)
        self.assertIsInstance(list(items)[0][1][0], tuple)

    async def test_get_update(self):
        u = await self.parser.get_update()
        self.assertIsInstance(u, str)
        self.assertRegex(u, r"Обновлено: \d{2}\.\d{2}\.\d{4} в \d{2}:\d{2}\.")

    async def test_get_exact_update(self):
        u = await self.parser.get_exact_update()
        self.assertIsInstance(u, tuple)
        self.assertRegex(u[0], r"\d{2}\.\d{2}\.\d{4}")
        self.assertRegex(u[1], r"\d{2}:\d{2}")

    async def test_get_day(self):
        d = await self.parser.get_day()
        self.assertIsInstance(d, str)
        self.assertRegex(d, r"\d{2}\.\d{2}\.\d{4} [А-Яа-я]{2}")


class TestWeekParser(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.parser = WeekParser("544")

    async def asyncTearDown(self):
        await self.parser.session.close()

    async def test_get_week(self):
        d = await self.parser.get_week()
        self.assertIsInstance(d, dict)
        self.assertGreater(len(d), 0)
        for k, v in d.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, list)
            self.assertIsInstance(v[0], tuple)
            self.assertIsInstance(v[0][1], tuple | None)
            self.assertRegex(k, r"\d{2}\.\d{2}\.\d{4} [А-Яа-я]{2}-(1|2)")

    async def test_get_update(self):
        u = await self.parser.get_update()
        self.assertIsInstance(u, str)
        self.assertRegex(u, r"Обновлено: \d{2}\.\d{2}\.\d{4} в \d{2}:\d{2}\.")

    async def test_get_exact_update(self):
        u = await self.parser.get_exact_update()
        self.assertIsInstance(u, tuple)
        self.assertRegex(u[0], r"\d{2}\.\d{2}\.\d{4}")
        self.assertRegex(u[1], r"\d{2}:\d{2}")


class TestMainParser(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.parser = MainParser("544")

    async def asyncTearDown(self):
        await self.parser.session.close()

    async def test_get_main(self):
        d = await self.parser.get_week()
        self.assertIsInstance(d, dict)
        self.assertGreater(len(d), 0)
        for k, v in d.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, list)
            self.assertIsInstance(v[0], tuple)
            self.assertIsInstance(v[0][1], tuple | None)
            self.assertRegex(k, r"[А-Яа-я]{2}-?2?")


if __name__ == "__main__":
    main()
