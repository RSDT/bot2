import sys

import settings
import authenticator
import logging
import Updates


def void_no_crash():
    def decorate(func):
        def call(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                type_, value_, traceback_ = sys.exc_info()
                print(traceback_)
                print(str(e))
                updates = Updates.get_updates()
                if func is not None:
                    logging.error(str(e) + '\n' + func.__name__)
                    updates.error(e, func.__name__,
                                  (type_, value_, traceback_))
                else:
                    logging.error(str(e) + '\nIk weet het niet meer.')
                    updates.error(e, '\nIk weet het niet meer.')
        return call

    return decorate
updater = None


def setUpdater(updater1):
    global updater
    updater = updater1


def authenticate():
    def decorate(func):
        def call(bot, update):
            global updater

            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            username = update.message.from_user.name
            chat_name = update.message.chat.title or (
                update.message.chat.first_name + ' ' +
                (update.message.chat.last_name or ''))
            if authenticator.authenticate_chat(user_id, chat_id,
                                               settings.Settings().SLEUTEL,
                                               username, chat_name):
                return func(bot, update)
            else:
                if type(chat_id) == int and chat_id > 0:
                    bot.sendMessage(chat_id,
                                    "je bent niet geverifierd! stuur een "
                                    "berichtje in een geverifiërde "
                                    "groepschat of naar de HB om je te "
                                    "verifiëren.")
                else:
                    mesg_id = update.message.message_id
                    bot.sendMessage(chat_id,
                                    "Deze groepsapp is niet geverifeerd. "
                                    "Stuur een berichtje naar de HB om deze "
                                    "groep te verifiëren.",
                                    reply_to_message_id=mesg_id)
                return None
        return call

    return decorate
