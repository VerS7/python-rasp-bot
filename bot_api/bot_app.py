"""
Основная логика приложения.
"""
from os import getenv, path

from rasp_api.schedule import ScheduleImageGenerator
from rasp_api.parsing import TagsParser

from bot_api.async_bot import AsyncVkBot, GREETING_TEXT
from bot_api.chats_connector import Chats
from bot_api.notificator import Notificator
from bot_api.utility import image_to_bytes
from bot_api.keyboard import get_keyboard_string, BASIC_KEYBOARD

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=path.join(path.dirname(path.abspath(__file__)), "../files/.env"))
except ModuleNotFoundError:
    pass


token = getenv("VK_TOKEN")
pub_id = int(getenv("PUBLIC_ID"))
prefixes = "!$#%^&*"

ChatSystem = Chats()  # Подключенные к оповещению чаты
Tags = TagsParser()  # Названия групп и тэги
ImageGenerator = ScheduleImageGenerator()  # Генератор изображений с расписанием
Notifier = Notificator(ChatSystem, ImageGenerator, timings=["07:00", "19:00"])  # Система оповещений
BotApp = AsyncVkBot(token, pub_id, admin_ids=[406579945], notificator=Notifier)  # Бот
basic_keyboard = get_keyboard_string(BASIC_KEYBOARD)  # Стандартная Not-Inline клавиатура


@BotApp.command(command="инфо", keyboard=basic_keyboard)
async def send_info(peer, args):
    """
    Вовращает стандартную информацию из info.txt
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    return peer, GREETING_TEXT


@BotApp.command(command="расп", placeholder="Подождите, идёт обработка...",
                keyboard=basic_keyboard)
async def send_daily(peer, args):
    """
    Вовращает ежедневное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if ChatSystem.in_chats(peer):
            groupname = ChatSystem.get_group(peer)
            return peer, \
                f"Ежедневное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_daily(groupname))
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await Tags.validate(args[0])
        if group:
            groupname = group[0]
            return peer, \
                f"Ежедневное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_daily(groupname))
    return peer, "Неверный или отсутствует номер группы."


@BotApp.command(command="нрасп", placeholder="Подождите, идёт обработка...",
                keyboard=basic_keyboard)
async def send_weekly(peer, args):
    """
    Вовращает ежеднедельное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if ChatSystem.in_chats(peer):
            groupname = ChatSystem.get_group(peer)
            return peer, \
                f"Недельное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_week(groupname))
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await Tags.validate(args[0])
        if group:
            groupname = group[0]
            return peer, \
                f"Недельное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_week(groupname))
    return peer, "Неверный или отсутствует номер группы."


@BotApp.command(command="орасп", placeholder="Подождите, идёт обработка...",
                keyboard=basic_keyboard)
async def send_main(peer, args):
    """
    Вовращает основное расписание по номеру группы или подключенному к чату номеру.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        if ChatSystem.in_chats(peer):
            groupname = ChatSystem.get_group(peer)
            return peer, \
                f"Основное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_main(groupname))
        return peer, "К данному диалогу не подключён номер группы."

    if args is not None:
        group = await Tags.validate(args[0])

        if group:
            groupname = group[0]
            return peer, \
                f"Основное расписание для группы {groupname}.", \
                image_to_bytes(await ImageGenerator.create_main(groupname))
    return peer, "Неверный или отсутствует номер группы."


@BotApp.command(command="группы", keyboard=basic_keyboard)
async def send_groups(peer, args):
    """
    Возвращает в чат все доступные к вызову номера групп
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    groups = '\n'.join(await Tags.parse_tags())
    return peer, f"Доступные группы: \n{groups}."


@BotApp.command(command="подключить")
async def notify_connect(peer, args):
    """
    Подключает конкретный чат к номеру группы.
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if ChatSystem.in_chats(peer):
        return peer, f"Данный чат уже подключён с номером группы: {ChatSystem.get_group(peer)}"

    if args is None:
        return peer, "Отсутствует номер группы."

    validated = await Tags.validate(args[0])
    if validated:
        group = validated[0]
        ChatSystem.add_group(peer, group)
        return peer, f"К чату с ID {peer} подключена группа {group}"

    return peer, "Неправильный номер группы."


@BotApp.command(command="отключить")
async def notify_disconnect(peer, args):
    """
    Отключает чат от номера группы. Вызывается без аргументов
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    group = ChatSystem.remove_chat(peer)

    if group is not None:
        return peer, f"Данный чат отключён от группы: {group}"

    return peer, "Данный чат не подключён к системе оповещений."


@BotApp.command(command="admin", admin=True)
async def admin_manage(peer, args):
    """
    Debug админ система
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    if args is None:
        return peer, "admin <command>\n" \
                     "mypeer: peer_id чата\n" \
                     "allchats: все привязанные чаты"

    match args[0]:
        case "mypeer":
            return peer, f"Peer ID: {peer}"

        case "allchats":
            return peer, \
                "\n".join([f"{chat[1]} : {chat[0]}" for chat in ChatSystem.get_chats().items()])

        case _:
            return peer, "Данная команда не определена."
