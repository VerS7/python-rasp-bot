"""
Основная логика приложения.
"""

from os import getenv, path

from loguru import logger

from rasp_api.schedule import ScheduleImageGenerator
from rasp_api.parsing import TagsParser

from .async_bot import AsyncVkBot, Context, GREETING_TEXT
from .chats_connector import JsonChatsConnector as Chats
from .services import NotificatorService
from .utility import image_to_bytes
from .keyboard import get_keyboard_string, BASIC_KEYBOARD, EMPTY_KEYBOARD

try:
    from dotenv import load_dotenv

    load_dotenv(
        dotenv_path=path.join(path.dirname(path.abspath(__file__)), "../../assets/.env")
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
empty_keyboard = get_keyboard_string(EMPTY_KEYBOARD)  # Пустая клавиатура


def is_peer_pm(peer: int) -> bool:
    """Проверка на то, является ли peer_id личного чата"""
    return not str(peer).startswith("2")


async def _send_daily(ctx_or_peer: int | Context) -> None:
    """Отправляет дневное расписание"""
    groupname = None
    peer = ctx_or_peer if isinstance(ctx_or_peer, int) else ctx_or_peer.peer
    keyboard = basic_keyboard if is_peer_pm(peer) else empty_keyboard
    msg_id = await app.send_message(
        peer_id=peer,
        message="Подождите, идёт обработка...",
        vk_keyboard=basic_keyboard,
    )  # айди сообщения для изменения

    if isinstance(ctx_or_peer, Context):
        if ctx_or_peer.args:
            validated = await tags.validate(ctx_or_peer.args[0])
            groupname = validated[0] if validated else None
        else:
            if chats.check(str(ctx_or_peer.peer)):
                groupname = chats.get(str(ctx_or_peer.peer))
    else:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))

    if groupname:
        image = await app.image_attachments(
            peer_id=peer,
            images=image_to_bytes(await image_generator.create_daily(groupname)),
        )
        if len(image) == 0:
            await app.send_message(
                peer_id=peer,
                message=f"Не удалось загрузить расписание. Попробуйте снова.",
                vk_keyboard=keyboard,
            )

        if msg_id != 0:
            await app.edit_message(
                peer_id=peer,
                message_id=msg_id,
                message=f"Ежедневное расписание для группы {groupname}.",
                attachment=image,
            )
        else:
            await app.send_message(
                peer_id=peer,
                message=f"Ежедневное расписание для группы {groupname}.",
                attachment=image,
                vk_keyboard=keyboard,
            )
        return

    if msg_id != 0:
        await app.edit_message(
            peer_id=peer,
            message_id=msg_id,
            message="Некорректный номер группы.",
        )
    else:
        await app.send_message(
            peer_id=peer,
            message="Некорректный номер группы.",
        )


async def _send_weekly(ctx_or_peer: int | Context) -> None:
    """Отправляет недельное расписание"""
    groupname = None
    peer = ctx_or_peer if isinstance(ctx_or_peer, int) else ctx_or_peer.peer
    keyboard = basic_keyboard if is_peer_pm(peer) else empty_keyboard
    msg_id = await app.send_message(
        peer_id=peer,
        message="Подождите, идёт обработка...",
        vk_keyboard=basic_keyboard,
    )  # айди сообщения для изменения

    if isinstance(ctx_or_peer, Context):
        if ctx_or_peer.args:
            validated = await tags.validate(ctx_or_peer.args[0])
            groupname = validated[0] if validated else None
        else:
            if chats.check(str(ctx_or_peer.peer)):
                groupname = chats.get(str(ctx_or_peer.peer))
    else:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))

    if groupname:
        images = await app.image_attachments(
            peer_id=peer,
            images=image_to_bytes(await image_generator.create_week(groupname)),
        )
        if len(images) == 0:
            await app.send_message(
                peer_id=peer,
                message=f"Не удалось загрузить расписание. Попробуйте снова.",
                vk_keyboard=keyboard,
            )

        if msg_id != 0:
            await app.edit_message(
                peer_id=peer,
                message_id=msg_id,
                message=f"Недельное расписание для группы {groupname}.",
                attachment=images,
            )
        else:
            await app.send_message(
                peer_id=peer,
                message=f"Недельное расписание для группы {groupname}.",
                attachment=images,
                vk_keyboard=keyboard,
            )
        return

    if msg_id != 0:
        await app.edit_message(
            peer_id=peer,
            message_id=msg_id,
            message="К данному чату не привязана группа.",
        )
    else:
        await app.send_message(
            peer_id=peer,
            message="К данному чату не привязана группа.",
            vk_keyboard=keyboard,
        )


async def _send_main(ctx_or_peer: int | Context) -> None:
    """Отправляет основное расписание"""
    groupname = None
    peer = ctx_or_peer if isinstance(ctx_or_peer, int) else ctx_or_peer.peer
    keyboard = basic_keyboard if is_peer_pm(peer) else empty_keyboard
    msg_id = await app.send_message(
        peer_id=peer,
        message="Подождите, идёт обработка...",
        vk_keyboard=basic_keyboard,
    )  # айди сообщения для изменения

    if isinstance(ctx_or_peer, Context):
        if ctx_or_peer.args:
            validated = await tags.validate(ctx_or_peer.args[0])
            groupname = validated[0] if validated else None
        else:
            if chats.check(str(ctx_or_peer.peer)):
                groupname = chats.get(str(ctx_or_peer.peer))
    else:
        if chats.check(str(peer)):
            groupname = chats.get(str(peer))

    if groupname:
        images = await app.image_attachments(
            peer_id=peer,
            images=image_to_bytes(await image_generator.create_main(groupname)),
        )
        if len(images) == 0:
            await app.send_message(
                peer_id=peer,
                message=f"Не удалось загрузить расписание. Попробуйте снова.",
                vk_keyboard=keyboard,
            )

        if msg_id != 0:
            await app.edit_message(
                peer_id=peer,
                message_id=msg_id,
                message=f"Основное расписание для группы {groupname}.",
                attachment=images,
            )
        else:
            await app.send_message(
                peer_id=peer,
                message=f"Основное расписание для группы {groupname}.",
                attachment=images,
                vk_keyboard=keyboard,
            )
        return

    if msg_id != 0:
        await app.edit_message(
            peer_id=peer,
            message_id=msg_id,
            message="К данному чату не привязана группа.",
        )
    else:
        await app.send_message(
            peer_id=peer,
            message="К данному чату не привязана группа.",
            vk_keyboard=keyboard,
        )


async def _send_groups(ctx_or_peer: int | Context) -> None:
    """Отправляет группы"""
    peer = ctx_or_peer if isinstance(ctx_or_peer, int) else ctx_or_peer.peer
    keyboard = basic_keyboard if is_peer_pm(peer) else empty_keyboard
    groups = "\n".join(await tags.parse_tags())
    await app.send_message(peer_id=peer, message=groups, vk_keyboard=keyboard)


async def _send_info(ctx_or_peer: int | Context) -> None:
    """Отправляет стандартную информацию"""
    peer = ctx_or_peer if isinstance(ctx_or_peer, int) else ctx_or_peer.peer
    keyboard = basic_keyboard if is_peer_pm(peer) else empty_keyboard
    await app.send_message(peer_id=peer, message=GREETING_TEXT, vk_keyboard=keyboard)


# ------------------- Ивенты -------------------
@app.on_payload("start")
async def send_startup_event(peer: int):
    """Отправляет стандартную по кнопке Начать"""
    await app.send_message(
        peer_id=peer, message=GREETING_TEXT, vk_keyboard=basic_keyboard
    )


@app.on_payload("инфо")
async def send_info_event(peer: int):
    """Отправляет стандартную информацию по кнопке"""
    await _send_info(peer)


@app.on_payload("расп")
async def send_daily_event(peer: int):
    """Отправляет дневное расписание по кнопке"""
    await _send_daily(peer)


@app.on_payload("нрасп")
async def send_weekly_payload(peer: int):
    """Отправляет недельное расписание по кнопке"""
    await _send_weekly(peer)


@app.on_payload("орасп")
async def send_main_payload(peer: int):
    """Отправляет основное расписание по кнопке"""
    await _send_main(peer)


@app.on_payload("группы")
async def send_groups_payload(peer: int):
    """Отправляет группы по кнопке"""
    await _send_groups(peer)


# ----------------- Команды -------------------
@app.command(command="инфо")
async def send_info(ctx: Context):
    """
    Отправляет стандартную информацию из info.txt
    """
    await _send_info(ctx)


@app.command(command="расп")
async def send_daily(ctx: Context):
    """
    Отправляет ежедневное расписание по номеру группы или подключенному к чату номеру.
    """
    await _send_daily(ctx)


@app.command(command="нрасп")
async def send_weekly(ctx: Context):
    """
    Отправляет недельное расписание по номеру группы или подключенному к чату номеру.
    """
    await _send_weekly(ctx)


@app.command(command="орасп")
async def send_main(ctx: Context):
    """
    Отправляет основное расписание по номеру группы или подключенному к чату номеру.
    """
    await _send_main(ctx)


@app.command(command="группы")
async def send_groups(ctx: Context):
    """
    Отправляет все доступные к вызову номера групп
    """
    await _send_groups(ctx)


@app.command(command="подключить")
async def notify_connect(ctx: Context):
    """
    Подключает текущий чат к номеру группы.
    """
    if chats.check(str(ctx.peer)):
        await app.send_message(
            peer_id=ctx.peer,
            message=f"Данный чат уже подключён с номером группы: {chats.get(str(ctx.peer))}",
            vk_keyboard=basic_keyboard,
        )
        return

    if ctx.args is None:
        await app.send_message(
            peer_id=ctx.peer,
            message=f"Отсутствует номер группы.",
            vk_keyboard=basic_keyboard,
        )
        return

    validated = await tags.validate(ctx.args[0])
    if validated:
        group = validated[0]
        chats.add(str(ctx.peer), group)
        await app.send_message(
            peer_id=ctx.peer,
            message=f"К чату с ID {ctx.peer} подключена группа {group}",
            vk_keyboard=basic_keyboard,
        )
        logger.info(
            f"Подключен чат: {ctx.peer} к системе оповещений с группой: {group}"
        )
        return

    await app.send_message(
        peer_id=ctx.peer,
        message="Неправильный номер группы.",
        vk_keyboard=basic_keyboard,
    )


@app.command(command="отключить")
async def notify_disconnect(ctx: Context):
    """
    Отключает чат от номера группы. Вызывается без аргументов
    """
    group = chats.remove(str(ctx.peer))

    if group is not None:
        await app.send_message(
            peer_id=ctx.peer,
            message=f"Данный чат отключён от группы: {group}",
            vk_keyboard=basic_keyboard,
        )
        logger.info(f"Чат: {ctx.peer} отключен от системы оповещений. Группа: {group}")
        return

    await app.send_message(
        peer_id=ctx.peer,
        message="Данный чат не подключен к системе оповещений.",
        vk_keyboard=basic_keyboard,
    )


@app.command(command="admin", admin=True)
async def admin_manage(ctx: Context):
    """
    Debug админ-система
    """
    if ctx.args is None:
        await app.send_message(
            peer_id=ctx.peer,
            message="admin <subcommand>\n"
            "mypeer: peer id текущего чата\n"
            "allchats: все привязанные чаты\n"
            "rmkb: удалить клавиатуру\n"
            "test: тестовая команда",
        )
        return

    match ctx.args[0]:
        case "mypeer":
            await app.send_message(
                peer_id=ctx.peer,
                message=f"Peer ID: {ctx.peer}",
            )

        case "allchats":
            await app.send_message(
                peer_id=ctx.peer,
                message="\n".join(
                    [f"{chat[1]} : {chat[0]}" for chat in chats.get_all().items()]
                ),
            )

        case "test":
            await app.send_message(
                peer_id=ctx.peer,
                message="Test",
            )

        case "rmkb":
            await app.send_message(
                peer_id=ctx.peer,
                message="Клавиатура удалена.",
                vk_keyboard=get_keyboard_string(EMPTY_KEYBOARD),
            )

        case _:
            await app.send_message(
                peer_id=ctx.peer, message="Данная команда не определена."
            )
