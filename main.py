"""
main
"""
import asyncio
import threading

from bot_api.bot_app import *


async_event_loop = asyncio.new_event_loop()


def run_bot(event_loop):
    """
    :param event_loop: asyncio event loop
    """
    asyncio.set_event_loop(event_loop)
    BotApp.run()


def run_api_server(event_loop):
    """
    :param event_loop: asyncio event loop
    """
    raise NotImplementedError


main_thread = threading.Thread(target=run_bot, args=(async_event_loop,))


if __name__ == "__main__":
    main_thread.start()
    main_thread.join()
