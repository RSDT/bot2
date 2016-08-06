from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import tokens
import logging
import authenticator

DeelgebiedUpdates, SWITCH_REMINDERS, BUG_REPORT, SCOUTING_GROEP = range(4)


class MultipleConversationsError(Exception):
    pass


class NotCancelledError(Exception):
    pass


class State:
    states = dict()

    def __init__(self, bot, chat_id, user_id, command, callback_on_done):
        """

        :param chat_id:
        :param user_id:
        :param command:
        :raises MultipleConversationsError als de gebruiker al in een chat zit.
        """
        if (str(user_id) + str(chat_id)) in State.states:
            raise MultipleConversationsError()
        self.chat_id = chat_id
        self.bot = bot
        self.user_id = user_id
        self.initiate_command = command
        self._data = dict()
        self.canceled = False
        self._done = False
        self.callback = callback_on_done
        State.states[str(user_id) + str(chat_id)] = self

    def __setattr__(self, key, value):
        self._data[key] = value

    def __setitem__(self, key, value):
        self._data[key] = value

    def cancel(self):
        del State.states[str(self.user_id) + str(self.chat_id)]
        self.canceled = True

    def done(self):
        self.cancel()
        self._done = True
        self.callback(self)

    def __iter__(self):
        """

        :raises NotCancelledError
        """
        if not self._done:
            raise NotCancelledError()
        for key in self._data:
            yield key, self._data[key]


def create_updater():
    updater = Updater(token=tokens.bot_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('deelgebieden', deelgebied_updates))

    dp.add_handler(MessageHandler([Filters.text], conversation))
    return updater


def authenticate():
    def decorate(func):
        def call(bot, update): 
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            username = update.message.from_user.name
            chat_name = update.message.chat.title or (
                update.message.chat.first_name + ' ' + update.message.chat.last_name)
            if authenticator.authenticate_chat(user_id, chat_id, tokens.SLEUTEL, username, chat_name):
                func(bot, update)
            else:
                if type(chat_id) == int and chat_id > 0:
                    bot.sendMessage(chat_id,
                                    "je bent niet geverifierd! stuur een berichtje" +
                                    " in een geverifiërde groepschat of naar de HB om je te verifiëren.")
                else:
                    bot.sendMessage(chat_id,
                                    "Deze groepsapp is niet geverifeerd." +
                                    " Stuur een berichtje naar de HB om deze groep te verifiëren.",
                                    reply_to_message_id=update.message.message_id)

        return call
    return decorate


@authenticate()
def conversation(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    h = str(user_id) + str(chat_id)
    try:
        state = State.states[h]
    except KeyError:
        return
    command = state.initiate_command
    if command == DeelgebiedUpdates:
        deelgebied_conversation(bot, update, state)


###############################################################################
# conversation functions.                                                     #
#                                                                             #
###############################################################################
def deelgebied_conversation(bot, update, state):
    # TODO implement this
    pass


###############################################################################
# command functions.                                                          #
#                                                                             #
###############################################################################
@authenticate()
def cancel(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    h = str(user_id) + str(chat_id)
    try:
        state = State.states[h]
        state.cancel()
    except KeyError:
        bot.sendMessage(chat_id, "Er is geen commando actief.", reply_to_message_id=update.message.message_id)
    else:
        bot.sendMessage(chat_id, "Het commando is gestopt.", reply_to_message_id=update.message.message_id)


@authenticate()
def deelgebied_updates(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, DeelgebiedUpdates, change_updates)
        bot.sendMessage(chat_id, "Voor welk deelgebied moeten updates aan of uit staan?\nA, B, C, D, E, F, X",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)


###############################################################################
# callback functions.                                                         #
#                                                                             #
###############################################################################
def change_updates(state):
    # TODO implement this
    pass
