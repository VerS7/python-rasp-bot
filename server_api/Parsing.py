# -*- coding: utf-8 -*-
from rasp_api.Parsing import get_daily, get_update, get_day, URL_WEEKLY
from rasp_api.GatherTags import validate_groupname, get_tags
from typing import Union


def html_daily(groupname: str) -> Union[str, None]:
    """
    Создаёт html разметку из ежедневного расписания по номеру группы
    :param str groupname: название/номер группы
    :return: размеченное html расписание для api
    """
    validated = validate_groupname(groupname, get_tags(URL_WEEKLY))

    if validated is None:
        return None

    rasp = get_daily(validated)

    html = [f'<span style="font-size: 20px; font-weight: bold;">Расписание на {get_day()}</span><br>',
            f'<span style="font-size: 20px; font-weight: bold;">Группа: {validated}</span><br><br>']

    for elem in rasp:
        html.append(f'<span style="font-weight: bold; font-size: 16px;">{elem[0]} {elem[1]}</span><br>')
        if len(elem) > 2:
            html.append(f'<span style="font-size: 18px; font-weight: bold;">{elem[2]}</span><br>'
                        f'<span style="font-size: 15px; font-weight: bold;">{elem[3]}</span><br>'
                        f'<span style="font-size: 16px; font-weight: bold;">{elem[4]}</span><br>')
        html.append('<br>')
    html.append(f'<span style="font-size: 19px; font-weight: bold;">{get_update()}</span>')

    return "".join(html)

