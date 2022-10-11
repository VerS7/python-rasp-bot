import threading
import rasp_api
from VKbotBOT import RaspBot


"""Main thread"""
raspbot = RaspBot()
main_thread = threading.Thread(target=raspbot.main)
main_thread.start()

"""Announces thread"""
ann = rasp_api.Annunciator(raspbot.bot)
#annons_thread = threading.Thread(target=ann.run())
#annons_thread.start()

"""Updater thread"""
updater = rasp_api.UpdateListener(delay=1)
updater_thread = threading.Thread(target=updater.run)
updater_thread.start()
