# -*- coding: utf-8 -*-
"""
Функционал для серверных запросов.
"""
from typing import Union

from rasp_api.parsing import get_daily, get_update, get_day, URL_WEEKLY
from rasp_api.gather_tags import validate_groupname, get_tags


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

    html = [f'<span style="font-size: 20px; font-weight: bold;">Расписание на '
            f'{get_day()}'
            f'</span><br>',

            f'<span style="font-size: 20px; font-weight: bold;">Группа: '
            f'{validated}'
            f'</span><br><br>']

    for elem in rasp:
        html.append(f'<span style="font-weight: bold; font-size: 16px;">'
                    f'{elem[0]} {elem[1]}'
                    f'</span><br>')
        if len(elem) > 2:
            html.append(f'<span style="font-size: 18px; font-weight: bold;">{elem[2]}</span><br>'
                        f'<span style="font-size: 15px; font-weight: bold;">{elem[3]}</span><br>'
                        f'<span style="font-size: 16px; font-weight: bold;">{elem[4]}</span><br>')
        html.append('<br>')
    html.append(f'<span style="font-size: 19px; font-weight: bold;">{get_update()}</span>')

    return "".join(html)

