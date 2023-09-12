# -*- coding: utf-8 -*-
from .Parsing import *
from PIL import Image, ImageDraw, ImageFont


IMAGE_SIZE = (1200, 1500)
MAIN_IMAGE_FONT = ImageFont.truetype("impact.ttf", size=35)
OTHER_IMAGE_FONT = ImageFont.truetype("impact.ttf", size=50)
BG_IMAGE = "./raspback.png"


def prettify_for_image(schedule: dict) -> list:
    """
    Возвращает подготовленный для изображения список строк
    :param list schedule: список расписания конкретной группы
    """
    result = []
    for elem in schedule:
        result.append(" ".join(elem[0:2]))
        if len(elem) > 2:
            result.append("\n".join(elem[2::]))
        else:
            pass
        result.append("-" * 90)
    return result


def daily_image(groupname: str):
    """Расписание на день в картинке"""
    background = Image.open(BG_IMAGE)
    rasp_image = ImageDraw.Draw(background)

    parsed = parse_request(URL_DAILY)
    update = get_update(parsed)
    time = get_day(parsed)
    daily = prettify_for_image(get_daily_by_groupname(groupname, soup=parsed))

    rasp_image.text((460, 100), time, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((510, 160), groupname, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((120, 240), "\n".join(daily), font=MAIN_IMAGE_FONT, fill=(86, 131, 172))
    rasp_image.text((290, 1300), update, font=OTHER_IMAGE_FONT, fill=(86, 131, 172))
    background.save("gaysex.png")
    # return background.resize(IMAGE_SIZE)
#
# def weekreading(groupname: str, tags: dict, urltype='cg'):
#     """Недельное расписание ДИНО"""
#     url = 'http://dmitrov-dubna.ru/shedule/{0}{1}.htm'.format(urltype, GatherTags.tagsearch(groupname, tags))
#     api = requests.get(url)
#     content = api.text
#     soup = BeautifulSoup(content, 'html.parser')
#     group = soup.find('h1').get_text().encode('latin1').decode('cp1251')
#     update = soup.find('div', {'class': 'ref'}).get_text().encode('latin1').decode('cp1251')
#     soup = soup.findAll(['td', 'a', 'div'], {'class': {'hd', 'hd0', 'z1', 'z2', 'z3'}})
#     out = []
#     for tag in soup:
#         out.append(tag.get_text(strip=True, separator='|').encode('latin1').decode('cp1251'))
#     del out[0:8]
#     out = '|'.join(out).replace(':|', ': ').split('|')
#     return out, group, update
#
#
# def weekreading_chuck(lst):
#     """Разделение недельного расписания по дням"""
#     rasp = []
#     out = []
#     for x in lst:
#         if len(x) > 0:
#             out.append(x)
#         else:
#             rasp.append(out.copy())
#             out.clear()
#     for elem in rasp:
#         if len(elem) == 3:
#             rasp.pop(rasp.index(elem))
#     return rasp[0:7]
#
#
# def weekreading_img(groupname, background, tags, urltype='cg'):
#     """Недельное/основное расписание картинками"""
#     mainfont = ImageFont.truetype("impact.ttf", size=35)
#     otherfont = ImageFont.truetype("impact.ttf", size=50)
#     txt, group, update = Schedule.weekreading(groupname, tags, urltype=urltype)
#     lst = Schedule.weekreading_chuck(txt)
#     final = []
#     rasp = []
#     pilobjs = []
#     for elem in lst:
#         for line in elem:
#             if len(line.split(" ")) > 5:
#                 line = " ".join(line.split(" ")[0:5]) + "..." + "\n"
#             elif line == '6':
#                 line = '-' * 90 + '\n' + line + " Пара:\n"
#             elif "Пара" in line:
#                 line = '-' * 90 + '\n' + line + '\n'
#             else:
#                 line = line + '\n'
#             final.append(line)
#         rasp.append(final.copy())
#         final.clear()
#     for elem in rasp:
#         back = Image.open(background)
#         img = ImageDraw.Draw(back)
#         img.text((460, 100), elem[0], font=otherfont, fill=(86, 131, 172))
#         img.text((410, 160), group, font=otherfont, fill=(86, 131, 172))
#         img.text((120, 265), " ".join(elem[1:]), font=mainfont, fill=(86, 131, 172))
#         img.text((290, 1300), update.strip(), font=otherfont, fill=(86, 131, 172))
#         image = back.resize(Schedule.size)
#         pilobjs.append(image)
#     return pilobjs
