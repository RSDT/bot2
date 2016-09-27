import queue
import threading
import uuid

import time


class LockedException(Exception):
    pass


class NotLockedException(Exception):
    pass


class Update:
    '''
    hier kunnen items aan toegevoegd worden.
    uitlezen mag alleen als lock gezet is.
    wanneer de lock gezet is kan deze nooit meer verwijderd worden.
    '''
    cached_updates = queue.Queue()
    cached_updates_lock = threading.Lock()

    def __init__(self):
        self._lock = False
        self.data = []
        self.id = uuid.uuid4()
        self.start_time = time.time()
        self.end_time = None

    def locked(self):
        return self._lock

    def lock(self):
        self._lock = True
        self.end_time = time.time()
        Update.cached_updates.put(self)

    def add_item(self, item, type=None):
        if not self._lock:
            if isinstance(item, Item):
                self.data.append(item)
            elif type is not None:
                item = Item(item, type)
                self.data.append(item)
            else:
                raise TypeError('type unknown')
        else:
            raise LockedException('Update is already locked.')

    def __iter__(self):
        if self.locked:
            for item in self.data:
                yield item
        else:
            raise NotLockedException('update not locked yet')

    @staticmethod
    def get_updates():
        while True:
            try:
                yield Update.cached_updates.get(timeout=5)
            except queue.Empty:
                return


class Item:
    def __init__(self, data, type):
        self.data = data
        self.type = type