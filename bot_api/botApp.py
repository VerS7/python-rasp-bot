from rasp_api.Schedule import daily_image, weekly_images
from rasp_api.GatherTags import get_tags
from rasp_api.Parsing import URL_WEEKLY
from rasp_api.groupValidator import get_tag, validate_groupname

from bot_api.asyncBot import AsyncVkBot
from bot_api.utility import *

from os import getenv
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../files/.env")
except ModuleNotFoundError:
    pass


t = getenv("VK_TOKEN")
p = int(getenv("PUBLIC_ID"))
BotApp = AsyncVkBot(t, p)


# Возвращает расписание на день по группе в диалог
@BotApp.command(command="расп", replaceable=True, placeholder="Подождите, идёт обработка...")
async def send_daily(peer, args):
    if args is not None:
        groupname = validate_groupname(args[0])
        if groupname:
            return peer, f"Ежедневное расписание для группы {groupname}.", image_to_bytes(daily_image(groupname))
    return peer, "Неверный или отсутствует номер группы."


# Возвращает доступные группы в диалог
@BotApp.command(command="группы", replaceable=True, placeholder="Подождите, идёт обработка...")
async def send_groups(peer, args):
    groups = '\n'.join(get_tags(URL_WEEKLY).keys())
    return peer, f"Доступные группы: \n{groups}."


# @BotApp.command(command="неделя", replaceable=True, placeholder="Подождите, идёт обработка...")
# async def send_weekly(peer, args):
#     return peer, f"Тест. Команда:{message}", image_to_bytes(weekly_images("544"))


BotApp.run()
