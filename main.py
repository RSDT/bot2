import os
import pickle

from menu import create_updater, STARTUPFILE
import logging
import Updates
import time
import threading
import wrappers
from PythonApi.RPApi.Base import Api as RpApi
from settings import Settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %('
                           'message)s, %(lineno)s, %(filename)s', level=logging.DEBUG)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._mystop = threading.Event()

    @wrappers.void_no_crash()
    def stop(self):
        self._mystop.set()

    def stopped(self):
        return self._mystop.isSet()

    @wrappers.void_no_crash()
    def run(self):
        logging.debug('5min update thread started')
        updater = Updates.get_updates()
        while not self.stopped():
            try:
                updater.update()
            except Exception as e:
                logging.error('update error:  ' + str(e))
                updater.error(e, 'update_thread')
            start = time.time()
            end = time.time()
            while end-start < 60 and not self.stopped():
                di = 5
                time.sleep(di)
                end = time.time()
        logging.debug('1min update thread stopped')


def main():
    if os.path.isfile(STARTUPFILE):
        with open(STARTUPFILE, 'rb') as file:
            start_up_command = pickle.load(file)
        if start_up_command['command'] == 'stop':
            with open(STARTUPFILE, 'wb') as file:
                pickle.dump({'command': 'start'}, file)
            return
    sett = Settings()
    api = RpApi.get_instance(sett.rp_username, sett.rp_pass)
    api.login()
    updater = create_updater()
    t = StoppableThread()
    t.start()

    updater.start_polling()
    updates = Updates.get_updates()
    updates.add_stopable_thread(t)
    updates.add_bot(updater.bot)
    updates.to_all('De bot is weer opgestart')
    updater.idle()
    updater.stop()


if __name__ == "__main__":
    main()
