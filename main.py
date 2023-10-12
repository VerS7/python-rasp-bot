"""
main
"""
import asyncio
import threading

from bot_api.bot_app import *
from server_api.server_app import run_app


async_event_loop = asyncio.new_event_loop()


def run_bot(event_loop):
    """
    :param event_loop: asyncio event loop
    """
    asyncio.set_event_loop(event_loop)
    BotApp.run()


main_thread = threading.Thread(target=run_bot, args=(async_event_loop,))
web_thread = threading.Thread(target=run_app)


if __name__ == "__main__":
    main_thread.start()
    web_thread.start()
    main_thread.join()
    web_thread.join()
