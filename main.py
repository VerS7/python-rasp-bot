import threading
import rasp_api
from VKbotBOT import RaspBot


"""Main thread"""
bot = RaspBot()
main_thread = threading.Thread(target=bot.main)
main_thread.start()

"""Updater thread"""
updater = rasp_api.UpdateListener(delay=1)
updater_thread = threading.Thread(target=updater.run)
updater_thread.start()
