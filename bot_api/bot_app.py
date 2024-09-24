"""
Основная логика приложения.
"""

from os import getenv, path

from rasp_api.schedule import ScheduleImageGenerator
from rasp_api.parsing import TagsParser

from bot_api.async_bot import AsyncVkBot, GREETING_TEXT
from bot_api.chats_connector import JsonChatsConnector as Chats
from bot_api.services import NotificatorService
from bot_api.utility import image_to_bytes
from bot_api.keyboard import get_keyboard_string, BASIC_KEYBOARD

try:
    from dotenv import load_dotenv

    load_dotenv(
        dotenv_path=path.join(path.dirname(path.abspath(__file__)), "../files/.env")
    )
except ModuleNotFoundError:
    pass

token = getenv("VK_TOKEN")
pub_id = int(getenv("PUBLIC_ID"))
prefixes = "!$#%^&*"

chats = Chats()  # Подключенные к оповещению чаты
tags = TagsParser()  # Названия групп и тэги
image_generator = ScheduleImageGenerator()  # Генератор изображений с расписанием
notificator = NotificatorService(
    chats, image_generator, timings=["07:00", "19:00"]
)  # Система оповещений
app = AsyncVkBot(
    token, pub_id, prefixes, admin_ids=[406579945], services=[notificator]
)  # Бот
basic_keyboard = get_keyboard_string(
    BASIC_KEYBOARD
)  # Стандартная Not-Inline клавиатура


@app.command(command="инфо", keyboard=basic_keyboard)
async def send_info(peer, args):
    """
    Вовращает стандартную информацию из info.txt
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    return peer, GREETING_TEXT


@app.command(
    command="расп", placeholder="Подождите, идёт обработка...", keyboard=basic_keyboard
)
async def send_daily(peer, args):
    """
    Вовращает ежедневное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))
            return (
                peer,
                f"Ежедневное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_daily(groupname)),
            )
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await tags.validate(args[0])
        if group:
            groupname = group[0]
            return (
                peer,
                f"Ежедневное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_daily(groupname)),
            )
    return peer, "Неверный или отсутствует номер группы."


@app.command(
    command="нрасп", placeholder="Подождите, идёт обработка...", keyboard=basic_keyboard
)
async def send_weekly(peer, args):
    """
    Вовращает ежеднедельное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))
            return (
                peer,
                f"Недельное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_week(groupname)),
            )
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await tags.validate(args[0])
        if group:
            groupname = group[0]
            return (
                peer,
                f"Недельное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_week(groupname)),
            )
    return peer, "Неверный или отсутствует номер группы."


@app.command(
    command="орасп", placeholder="Подождите, идёт обработка...", keyboard=basic_keyboard
)
async def send_main(peer, args):
    """
    Вовращает основное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))
            return (
                peer,
                f"Основное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_main(groupname)),
            )
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await tags.validate(args[0])

        if group:
            groupname = group[0]
            return (
                peer,
                f"Основное расписание для группы {groupname}.",
                image_to_bytes(await image_generator.create_main(groupname)),
            )
    return peer, "Неверный или отсутствует номер группы."


@app.command(command="группы", keyboard=basic_keyboard)
async def send_groups(peer, args):
    """
    Возвращает в чат все доступные к вызову номера групп
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    groups = "\n".join(await tags.parse_tags())
    return peer, f"Доступные группы: \n{groups}."


@app.command(command="подключить")
async def notify_connect(peer, args):
    """
    Подключает конкретный чат к номеру группы.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if chats.check(str(peer)):
        return (
            peer,
            f"Данный чат уже подключён с номером группы: {chats.get(peer)}",
        )

    if args is None:
        return peer, "Отсутствует номер группы."

    validated = await tags.validate(args[0])
    if validated:
        group = validated[0]
        chats.add(peer, group)
        return peer, f"К чату с ID {peer} подключена группа {group}"

    return peer, "Неправильный номер группы."


@app.command(command="отключить")
async def notify_disconnect(peer, args):
    """
    Отключает чат от номера группы. Вызывается без аргументов
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    group = chats.remove(str(peer))

    if group is not None:
        return peer, f"Данный чат отключён от группы: {group}"

    return peer, "Данный чат не подключён к системе оповещений."


@app.command(command="admin", admin=True)
async def admin_manage(peer, args):
    """
    Debug админ система
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        return (
            peer,
            "admin <command>\n"
            "mypeer: peer_id чата\n"
            "allchats: все привязанные чаты",
        )

    match args[0]:
        case "mypeer":
            return peer, f"Peer ID: {peer}"

        case "allchats":
            return peer, "\n".join(
                [f"{chat[1]} : {chat[0]}" for chat in chats.get_all().items()]
            )

        case _:
            return peer, "Данная команда не определена."
