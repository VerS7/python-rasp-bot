# -*- coding: utf-8 -*-
import os
import glob
import requests
import re
import xlrd
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


class Schedule(object):
    """Размер выходных изображений"""
    size = (1200, 1500)
    """Функции с расписанием"""
    @staticmethod
    def rasparse(url):
        """Вычленение текста расписания с сайта по url"""
        try:
            api = requests.get(url)
            content = api.text
            soup = BeautifulSoup(content, 'html.parser')
            out = []
            soup = soup.select('.zgr') + soup.select('.inf') + soup.select('.ref')
            for tag in soup:
                out.append(tag.get_text(strip=True, separator='|').encode('latin1').decode('cp1251'))
            out = '|'.join(out).replace(':|', ': ').split('|')
            return out
        except Exception as e:
            print(e)

    @classmethod
    def weekreading(cls, groupname, tags, urltype='cg'):
        """Недельное расписание ДИНО"""
        try:
            url = 'http://dmitrov-dubna.ru/shedule/{0}{1}.htm'.format(urltype, GatherTags.tagsearch(groupname, tags))
            api = requests.get(url)
            content = api.text
            soup = BeautifulSoup(content, 'html.parser')
            group = soup.find('h1').get_text().encode('latin1').decode('cp1251')
            update = soup.find('div', {'class': 'ref'}).get_text().encode('latin1').decode('cp1251')
            soup = soup.findAll(['td', 'a', 'div'], {'class': {'hd', 'hd0', 'z1', 'z2', 'z3'}})
            out = []
            for tag in soup:
                out.append(tag.get_text(strip=True, separator='|').encode('latin1').decode('cp1251'))
            del out[0:8]
            out = '|'.join(out).replace(':|', ': ').split('|')
            return out, group, update
        except Exception as e:
            print(e)

    @classmethod
    def reading(cls, groupname):
        """Расписание на день в виде строки"""
        try:
            url = "http://dmitrov-dubna.ru/shedule/hg.htm"
            text = cls.rasparse(url)
            rasp = []
            flag = False
            rasp.append(str(text[0]) + '\n')
            for line in text:
                if groupname in line:
                    flag = True
                if flag is True:
                    if line == "6":
                        break
                    rasp.append(str(line) + '\n')
            rasp.append(str(text[len(text) - 1]) + '\n')
            return rasp
        except Exception as e:
            print(e)

    @classmethod
    def reading_img(cls, groupname, background):
        """Расписание на день в картинке"""
        try:
            mainfont = ImageFont.truetype("impact.ttf", size=35)
            otherfont = ImageFont.truetype("impact.ttf", size=50)
            back = Image.open(background)
            img = ImageDraw.Draw(back)
            txt = cls.reading(groupname)
            time = txt[0]
            group = txt[1]
            update = txt[len(txt) - 1]
            rasp = txt[2:len(txt) - 1]
            final = []
            for line in rasp:
                if len(line.split(" ")) > 5:
                    line = " ".join(line.split(" ")[0:5]) + "..." + "\n"
                elif "Пара" in line:
                    line = '-' * 90 + '\n' + line
                final.append(line)
            final[0] = " " + final[0]
            img.text((460, 100), time, font=otherfont, fill=(86, 131, 172))
            img.text((490, 160), group, font=otherfont, fill=(86, 131, 172))
            img.text((120, 265), " ".join(final), font=mainfont, fill=(86, 131, 172))
            img.text((290, 1300), update, font=otherfont, fill=(86, 131, 172))
            image = back.resize(cls.size)
            image.save('rasp_pic.png')
        except Exception as e:
            print(e)

    @staticmethod
    def weekreading_chuck(lst):
        """Разделение недельного расписания по дням"""
        try:
            rasp = []
            out = []
            for x in lst:
                if len(x) > 0:
                    out.append(x)
                else:
                    rasp.append(out.copy())
                    out.clear()
            for elem in rasp:
                if len(elem) == 3:
                    rasp.pop(rasp.index(elem))
            return rasp[0:7]
        except Exception as e:
            print(e)

    @classmethod
    def weekreading_img(cls, groupname, background, tags, urltype='cg'):
        """Недельное/основное расписание картинками"""
        try:
            mainfont = ImageFont.truetype("impact.ttf", size=35)
            otherfont = ImageFont.truetype("impact.ttf", size=50)
            txt, group, update = cls.weekreading(groupname, tags, urltype=urltype)
            lst = cls.weekreading_chuck(txt)
            final = []
            rasp = []
            for elem in lst:
                for line in elem:
                    if len(line.split(" ")) > 5:
                        line = " ".join(line.split(" ")[0:5]) + "..." + "\n"
                    elif line == '6':
                        line = '-' * 90 + '\n' + line + " Пара:\n"
                    elif "Пара" in line:
                        line = '-' * 90 + '\n' + line + '\n'
                    else:
                        line = line + '\n'
                    final.append(line)
                rasp.append(final.copy())
                final.clear()
            for elem in rasp:
                back = Image.open(background)
                img = ImageDraw.Draw(back)
                img.text((460, 100), elem[0], font=otherfont, fill=(86, 131, 172))
                img.text((410, 160), group, font=otherfont, fill=(86, 131, 172))
                img.text((120, 265), " ".join(elem[1:]), font=mainfont, fill=(86, 131, 172))
                img.text((290, 1300), update.strip(), font=otherfont, fill=(86, 131, 172))
                image = back.resize(cls.size)
                image.save(f'{urltype}/{rasp.index(elem)}_{groupname}.png')
        except Exception as e:
            print(e)


class ExcelSchedule(object):
    """Высота расписаний в excel-файле"""
    group_count = 10
    """Функции excel-расписания"""
    @staticmethod
    def split(a, n):
        """Деление списков"""
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    @classmethod
    def flatten(cls, L):
        """Развёртка вложенных списков"""
        for item in L:
            if any(isinstance(i, list) for i in item):
                yield from cls.flatten(item)
            else:
                yield item

    @classmethod
    def excel_parse(cls, filename, count=group_count):
        """Парсинг эксель-файла на блоки с расписанием каждой группы"""
        try:
            file = xlrd.open_workbook(filename)
            sheet = file.sheet_by_index(0)
            vals = [sheet.row_values(rownum) for rownum in range(6, sheet.nrows)]
            time = ''.join(sheet.row_values(1)).strip('на ')
            rasps = []
            for column in range(0, 4):
                rasp = []
                for elem in vals:
                    x = list(cls.split(elem[3::], 4))
                    rasp.append(x[column])
                splited = list(cls.split(rasp, count))
                for i in splited:
                    f = list(cls.split(i[1::], 6))
                    h = list(cls.flatten(f))
                    out = [''.join(i[0]) + '\n', ''.join(i[0]) + '\n']
                    for c in range(0, len(h)):
                        if c % 2 == 0:
                            out.append(f'Пара:\n'), out.append(''.join(h[c][::2]) + '\n'), out.append(''.join(h[c][2::]) + '\n')
                        else:
                            out.append(''.join(h[c][::2]) + '\n'), out.append(''.join(h[c][2::]) + '\n')
                    final = []
                    for j in out:
                        if j != '\n':
                            final.append(j)
                    final[0] = time
                    rasps.append(final)
            return rasps
        except Exception as e:
            print(e)

    @staticmethod
    def excel_reading(groupname, excel_rasp):
        """Возвращает расписание группы по тэгу"""
        for elem in excel_rasp:
            if groupname in elem[1]:
                return elem

    @classmethod
    def excel_reading_img(cls, groupname, background, filename):
        """Расписание на день в картинке"""
        try:
            mainfont = ImageFont.truetype("impact.ttf", size=35)
            otherfont = ImageFont.truetype("impact.ttf", size=50)
            back = Image.open(background)
            img = ImageDraw.Draw(back)
            txt = cls.excel_reading(groupname, cls.excel_parse(filename))
            time = txt[0]
            group = txt[1]
            rasp = txt[2:len(txt)]
            final = []
            for line in rasp:
                if len(line.split(" ")) > 5:
                    line = " ".join(line.split(" ")[0:5]) + "..." + "\n"
                elif "Пара" in line:
                    line = '-' * 90 + '\n' + line
                final.append(line)
            final[0] = " " + final[0]
            img.text((350, 100), time, font=otherfont, fill=(86, 131, 172))
            img.text((490, 160), group, font=otherfont, fill=(86, 131, 172))
            img.text((120, 265), " ".join(final), font=mainfont, fill=(86, 131, 172))
            image = back.resize(Schedule.size)
            image.save('exc_rasp_pic.png')
        except Exception as e:
            print(e)


class Util(object):
    """Утилитарные функции"""

    @staticmethod
    def img_clear(path):
        """Удаление всех картинок по заданному пути"""
        try:
            imgs = glob.glob(path)
            for x in imgs:
                os.remove(x)
        except Exception as e:
            print(e)


class GatherTags(object):
    """Функции обработки названий групп/тэгов"""

    @staticmethod
    def tagsparse():
        """Получение названий групп и тэгов"""
        try:
            url = 'http://dmitrov-dubna.ru/shedule/cg.htm'
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

    @classmethod
    def tagsprettify(cls):
        """Создание словаря Группа:Тэг"""
        try:
            x, z = cls.tagsparse()
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
    def tagsearch(groupname, tags):
        """Возвращает первый найденный тэг по номеру группы"""
        try:
            for i in tags:
                if groupname in i:
                    return tags.get(i)
            return None
        except Exception as e:
            print(e)

    @classmethod
    def grouplist_create(cls):
        """Создаёт список групп"""
        final = []
        for i in cls.tagsprettify():
            final.append(i)
        return final

    @staticmethod
    def groupname_validation(groupname, grouplist):
        """Проверяет наличие группы в списке групп"""
        try:
            for i in grouplist:
                if groupname.upper() in i:
                    return True
            return False
        except Exception as e:
            print(e)
            return False
