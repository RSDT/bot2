from commands import create_updater
import logging
import Updates
import time
import threading

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s, %(lineno)s', level=logging.INFO)

running = True


def update_thread():
    global running
    updater = Updates.get_updates()
    while running:
        try:
            updater.update()
        except Exception as e:
            logging.error('update error:  ' + str(e))
            updater.error(e, 'update_thread')
        time.sleep(300)


def main():
    global running
    updater = create_updater()
    t = threading.Thread(target=update_thread)
    t.start()
    updater.start_polling()
    updater.idle()
    running = False
    t.join()

if __name__ == "__main__":
    main()
