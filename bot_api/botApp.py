from rasp_api.Schedule import daily_image, weekly_images
from rasp_api.GatherTags import get_tags
from rasp_api.Parsing import URL_WEEKLY
from rasp_api.groupValidator import get_tag, validate_groupname

from bot_api.asyncBot import AsyncVkBot
from bot_api.chatsConnector import Chats
from bot_api.utility import *

from os import getenv
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../files/.env")
except ModuleNotFoundError:
    pass


token = getenv("VK_TOKEN")
pub_id = int(getenv("PUBLIC_ID"))

BotApp = AsyncVkBot(token, pub_id)  # Бот
ChatSystem = Chats()


# Возвращает расписание на день по группе в диалог
@BotApp.command(command="расп", replaceable=True, placeholder="Подождите, идёт обработка...")
async def send_daily(peer, args):
    if args is None:
        if ChatSystem.in_chats(peer):
            groupname = ChatSystem.get_group(peer)
            return peer, f"Ежедневное расписание для группы {groupname}.", image_to_bytes(daily_image(groupname))

    if args is not None:
        groupname = validate_groupname(args[0])
        if groupname:
            return peer, f"Ежедневное расписание для группы {groupname}.", image_to_bytes(daily_image(groupname))
    return peer, "Неверный или отсутствует номер группы."


@BotApp.command(command="неделя", replaceable=True, placeholder="Подождите, идёт обработка...")
async def send_weekly(peer, args):
    if args is None:
        if ChatSystem.in_chats(peer):
            groupname = ChatSystem.get_group(peer)
            return peer, f"Недельное расписание для группы {groupname}.", image_to_bytes(weekly_images(get_tag(groupname)))

    if args is not None:
        groupname = validate_groupname(args[0])
        if groupname:
            return peer, f"Недельное расписание для группы {groupname}.", image_to_bytes(weekly_images(get_tag(groupname)))
    return peer, "Неверный или отсутствует номер группы."


# Возвращает доступные группы в диалог
@BotApp.command(command="группы", replaceable=True, placeholder="Подождите, идёт обработка...")
async def send_groups(peer, args):
    groups = '\n'.join(get_tags(URL_WEEKLY).keys())
    return peer, f"Доступные группы: \n{groups}."


# Подключает диалог к системе оповещений/быстрых вызовов
@BotApp.command(command="подключить")
async def notify_connect(peer, args):
    if ChatSystem.in_chats(peer):
        return peer, f"Данный чат уже подключён с номером группы: {ChatSystem.get_group(peer)}"

    if args is None:
        return peer, "Отсутствует номер группы."

    validated = validate_groupname(args[0])
    if validated:
        ChatSystem.add_group(peer, validated)
        return peer, f"К чату с ID {peer} подключена группа {validated}"

    return peer, f"Неправильный номер группы."


# Отключает диалог от системы оповещений/быстрых вызовов
@BotApp.command(command="отключить")
async def notify_disconnect(peer, args):
    group = ChatSystem.remove_chat(peer)

    if group is not None:
        return peer, f"Данный чат отключён от группы: {group}"

    return peer, f"Данный чат не подключён к системе оповещений."


# @BotApp.command(command="неделя", replaceable=True, placeholder="Подождите, идёт обработка...")
# async def send_weekly(peer, args):
#     return peer, f"Тест. Команда:{message}", image_to_bytes(weekly_images("544"))

BotApp.run()
