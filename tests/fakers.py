from queue import Queue, Empty

import telegram
import datetime

class FakeBot:
    def __init__(self, *args, **kwargs):
        self.next_message_id = next_message_id()
        self.next_update_id = next_message_id()
        self.user = telegram.User(1234567890, 'Unittest')
        self.updates = Queue()

    def getUpdates(self, last_update_id, *args, **kwargs):
        updates = []
        try:
            while not self.updates.empty():
                updates.append(self.updates.get_nowait())
        except Empty:
            pass
        return updates

    def sendMessage(self, chat_id, message, *args, **kwargs):
        chat = telegram.Chat(chat_id, telegram.Chat.SUPERGROUP)
        message = telegram.Message(next(self.next_message_id), self.user,
                         datetime.datetime.now(), chat)
        return message

    def sendSticker(self, chat_id, *args, **kwargs):
        pass

    def sendLocation(self, chat_id, *args, **kwargs):
        pass

    def add_update(self, chat_id, text):
        chat = telegram.Chat(chat_id, telegram.Chat.SUPERGROUP)
        user = telegram.User(1234, 'test')
        message = telegram.Message(next(self.next_message_id), user,
                                   datetime.datetime.now(), chat, text=text)
        update = telegram.Update(next(self.next_update_id), message=message)
        self.updates.put_nowait(update)

def next_message_id():
    i = 0
    while True:
        yield i
        i+=1
