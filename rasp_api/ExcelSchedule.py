# -*- coding: utf-8 -*-


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
    def excel_reading_img(cls, groupname: str, background: str, filename: str) -> None:
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