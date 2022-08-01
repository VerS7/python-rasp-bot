# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from .Util import Util


class Schedule(object):
    """Размер выходных изображений"""
    size = (1200, 1500)
    """Функции с расписанием"""
    @staticmethod
    def rasparse(url: str) -> list:
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
    def weekreading(cls, groupname: str, tags: dict, urltype='cg') -> tuple:
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
    def reading(cls, groupname: str) -> list:
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
    def reading_img(cls, groupname: str, background: str) -> None:
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
            image.save(f'temp/rasp.png')
        except Exception as e:
            print(e)

    @staticmethod
    def weekreading_chuck(lst: list) -> list:
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
    def weekreading_img(cls, groupname: str, background: str, tags: dict, urltype='cg') -> None:
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
            Util.img_clear(f'temp/{urltype}/*')
            for elem in rasp:
                back = Image.open(background)
                img = ImageDraw.Draw(back)
                img.text((460, 100), elem[0], font=otherfont, fill=(86, 131, 172))
                img.text((410, 160), group, font=otherfont, fill=(86, 131, 172))
                img.text((120, 265), " ".join(elem[1:]), font=mainfont, fill=(86, 131, 172))
                img.text((290, 1300), update.strip(), font=otherfont, fill=(86, 131, 172))
                image = back.resize(cls.size)
                image.save(f'temp/{urltype}/{rasp.index(elem)}_{groupname}.png')
        except Exception as e:
            print(e)