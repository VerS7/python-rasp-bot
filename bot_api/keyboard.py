"""
Клавиатуры для ВК диалогов.
"""

import json


BASIC_KEYBOARD = {
    "inline": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Дневное расписание",
                    "payload": {"command": "расп"},
                },
                "color": "secondary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Недельное расписание",
                    "payload": {"command": "нрасп"},
                },
                "color": "secondary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Основное расписание",
                    "payload": {"command": "орасп"},
                },
                "color": "secondary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Группы",
                    "payload": {"command": "группы"},
                },
                "color": "secondary",
            },
            {
                "action": {
                    "type": "text",
                    "label": "Помощь",
                    "payload": {"command": "инфо"},
                },
                "color": "secondary",
            },
        ],
    ],
}


EMPTY_KEYBOARD = {"buttons": [], "one_time": True}


__INLINE_COMMAND_KEYBOARD = {
    "inline": True,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Да",
                    "payload": {"command": "#"},
                },
                "color": "positive",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Нет",
                    "payload": {"command": "$"},
                },
                "color": "negative",
            }
        ],
    ],
}


def get_keyboard_string(keyboard: dict) -> str:
    """
    :param dict keyboard: VK Keyboard в виде dict.
    :return: jsonified строка
    """
    return json.dumps(keyboard)
