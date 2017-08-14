from threading import Lock

from telegram import Chat

import settings
from PythonApi.RPApi.Base import Api as RpApi


@settings.Singleton
class IdsObserver:
    def __init__(self):
        self.group_chats = dict()
        self.user_buffer = dict()
        self.users_lock = Lock()

    def add_user_to_buffer(self, telegram_id, first_name, last_name, username):
        with self.users_lock:
            self.user_buffer[telegram_id] = {"telegramID": telegram_id,
                                             "telegramVoornaam":     first_name or 'onbekend',
                                             "telegramAchternaam":    last_name or 'onbekend',
                                             "telegramGebruikersnaam":     username or 'onbekend'}

    def add_group_chat(self, chat_type, chat_id, chat_name):
        if chat_type != Chat.PRIVATE:
            self.group_chats[chat_id] = chat_name

    def send_users_buffer(self):
        api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
        with self.users_lock:
            for tid in self.user_buffer:
                try:
                    api.send_telegram_user(**self.user_buffer[tid])
                except Exception as e:
                    raise e
            self.user_buffer.clear()

    def getName(self, userId):
        user = self.user_buffer.get(userId, None)
        if user is None:
            return 'not in list'
        else:
            return user["telegramVoornaam"] + ' ' + user["telegramAchternaam"] + ';' + user["telegramGebruikersnaam"]
