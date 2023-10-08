# -*- coding: utf-8 -*-
"""
Основная логика приложения.
"""
from os import getenv, path

from rasp_api.Schedule import daily_image, weekly_images
from rasp_api.gather_tags import get_tags
from rasp_api.Parsing import URL_WEEKLY
from rasp_api.group_validate import get_tag, validate_groupname

from bot_api.async_bot import AsyncVkBot
from bot_api.chats_connector import Chats
from bot_api.notificator import Notificator
from bot_api.utility import image_to_bytes

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=path.join(path.dirname(path.abspath(__file__)), "../files/.env"))
except ModuleNotFoundError:
    pass


token = getenv("VK_TOKEN")
pub_id = int(getenv("PUBLIC_ID"))

ChatSystem = Chats()  # Подключенные к оповещению чаты
Notifier = Notificator(ChatSystem, timings=["01:45"])  # Система оповещений
BotApp = AsyncVkBot(token, pub_id, admin_ids=[406579945], notificator=Notifier)  # Бот


# Возвращает расписание на день по группе в диалог
@BotApp.command(command="расп", replaceable=True, placeholder="Подождите, идёт обработка...")
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
                image_to_bytes(daily_image(groupname))

    if args is not None:
        groupname = validate_groupname(args[0])
        if groupname:
            return peer, \
                f"Ежедневное расписание для группы {groupname}.", \
                image_to_bytes(daily_image(groupname))
    return peer, "Неверный или отсутствует номер группы."


# Возвращает недельное расписание по группе в диалог
@BotApp.command(command="неделя", replaceable=True, placeholder="Подождите, идёт обработка...")
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
                image_to_bytes(weekly_images(get_tag(groupname)))

    if args is not None:
        groupname = validate_groupname(args[0])
        if groupname:
            return peer, \
                f"Недельное расписание для группы {groupname}.", \
                image_to_bytes(weekly_images(get_tag(groupname)))
    return peer, "Неверный или отсутствует номер группы."


# Возвращает доступные группы в диалог
@BotApp.command(command="группы")
async def send_groups(peer, args):
    """
    Возвращает в чат все доступные к вызову номера групп
    :param peer: id чата
    :param args: аргументы, переданные при вызове команды через чат
    """
    groups = '\n'.join(get_tags(URL_WEEKLY).keys())
    return peer, f"Доступные группы: \n{groups}."


# Подключает диалог к системе оповещений/быстрых вызовов
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

    validated = validate_groupname(args[0])
    if validated:
        ChatSystem.add_group(peer, validated)
        return peer, f"К чату с ID {peer} подключена группа {validated}"

    return peer, "Неправильный номер группы."


# Отключает диалог от системы оповещений/быстрых вызовов
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


# Админ-функционал
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
