from telegram.ext import Updater,  MessageHandler, Filters
import tokens
import Updates
from wrappers import void_no_crash, authenticate
from CommandHandlerWithHelp import CommandHandlerWithHelp

DeelgebiedUpdates, SWITCH_REMINDERS, BUG_REPORT,\
ErrorUpdates, NieuwsUpdates, SCOUTING_GROEP,\
PhotoUpdates, OpdrachtUpdates, HintUpdates\
    = range(9)


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
        self._data = dict()
        self.chat_id = chat_id
        self.bot = bot
        self.user_id = user_id
        self.initiate_command = command
        self.canceled = False
        self._done = False
        self.path = []
        self.state = 0
        self.callback = callback_on_done
        State.states[str(user_id) + str(chat_id)] = self

    def __getitem__(self, item):
        return self._data[item]

    @void_no_crash()
    def __setitem__(self, key, value):
        self._data[key] = value

    @void_no_crash()
    def cancel(self):
        del State.states[str(self.user_id) + str(self.chat_id)]
        self.canceled = True

    @void_no_crash()
    def next_state(self):
        self.state += 1

    @void_no_crash()
    def done(self):
        self.cancel()
        self._done = True
        self.callback(self)

    def get_state(self):
        return self.state

    def __iter__(self):
        """

        :raises NotCancelledError
        """
        if not self._done:
            raise NotCancelledError()
        for key in self._data:
            yield key, self._data[key]


def error_handler(bot, update, error):
    bot.sendMessage(update.message.chat_id, "er is in deze chat een error opgetreden:\n" + str(error))
    Updates.get_updates().error(error, "Updater")


def create_updater():
    updater = Updater(token=tokens.bot_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandlerWithHelp('cancel', cancel, 'verlaat het huidige commando'))
    dp.add_handler(CommandHandlerWithHelp('deelgebieden', deelgebied_updates, 'zet updates aan/uit voor vossen'))
    dp.add_handler(CommandHandlerWithHelp('error', error_updates, 'zet updates aan/uit voor errors'))
    dp.add_handler(CommandHandlerWithHelp('crash', crash, 'veroorzaak een test error'))
    dp.add_handler(CommandHandlerWithHelp('help', help, 'laat de helptext zien.'))
    dp.add_handler(CommandHandlerWithHelp('check_updates', check_updates, 'kijk welke updates aan staan in deze chat.'))
    dp.add_handler(CommandHandlerWithHelp('start', start, 'start de bot'))
    dp.add_handler(CommandHandlerWithHelp('nieuws', nieuws_updates, 'zet nieuws updates aan of uit'))
    dp.add_handler(CommandHandlerWithHelp('test', test, 'test of de bot online is.'))
    dp.add_handler(CommandHandlerWithHelp('opdrachten', opdrachten, 'zet opdracht updates aan of uit.'))
    dp.add_handler(CommandHandlerWithHelp('hints', hint_updates, 'zet hint updates aan of uit.'))
    dp.add_handler(MessageHandler([Filters.text], conversation))
    return updater


###############################################################################
# command functions.                                                          #
#                                                                             #
###############################################################################
def opdrachten(bot, update):
    """

            :param bot:
            :param update:
            :return:
            """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, OpdrachtUpdates, change_niews_updates)
        bot.sendMessage(chat_id, "Moeten opdracht updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'opdracht_update')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_opdracht_update')


@void_no_crash()
def test(bot, update):
    bot.sendMessage(update.message.chat_id, 'de bot is online')
    Updates.get_updates().botan.track(update.message, 'test')


@void_no_crash()
@authenticate()
def nieuws_updates(bot, update):
    """

        :param bot:
        :param update:
        :return:
        """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, NieuwsUpdates, change_niews_updates)
        bot.sendMessage(chat_id, "Moeten nieuws updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'nieuws_update')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_nieuws_update')


@void_no_crash()
@authenticate()
def check_updates(bot, update):
    message = 'updates staan aan voor:\n'
    for u in Updates.get_updates().check_updates(update.message.chat_id):
        message += u + '\n'
    bot.sendMessage(update.message.chat_id, message)
    Updates.get_updates().botan.track(update.message, 'check_update')


start_message = \
"""
Welkom Bij de Telegrambot voor de jotihunt van de RP.\n
Deze bot kun je gebruiken om informatie op te vragen tijdens de hunt.
of om updates te ontvangen tijdens de hunt.
Voor meer informatie : /help

Deze bot kan alleen gebruikt worden door de RP en daarom moet je eerst geverifiërd worden.
Dat kan je op 2 manieren doen:
Je zet een berichtje in een groepsapp en dan wordt je automatisch geverifiërd.
Of je stuurt hier een berichtje en vraagt of de homebase je wil verifieren.
"""

@void_no_crash()
def start(bot, update):
    bot.sendMessage(update.message.chat_id, start_message)
    Updates.get_updates().botan.track(update.message, 'start')


@void_no_crash()
def help(bot, update):
    message = start_message + "\n\n"
    for commando in CommandHandlerWithHelp.helps:
        message += '/' + commando + ' - ' + CommandHandlerWithHelp.helps[commando] + '\n'
    bot.sendMessage(update.message.chat_id, message)
    Updates.get_updates().botan.track(update.message, 'help')


@void_no_crash()
@authenticate()
def crash(bot, update):
    bot.sendMessage(update.message.chat_id, 'we gaan de bot proberen te crashen')
    Updates.get_updates().botan.track(update.message, '/crash')
    raise Exception("dit is een test")


@void_no_crash()
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
        Updates.get_updates().botan.track(update.message, 'incorrect_cancel')
    else:
        bot.sendMessage(chat_id, "Het commando is gestopt.", reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'cancel')


@void_no_crash()
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
        State(bot, chat_id, user_id, DeelgebiedUpdates, change_dg_updates)
        bot.sendMessage(chat_id, "Voor welk deelgebied moeten updates aan of uit staan?\nA, B, C, D, E, F, X",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'deelgebied')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_deelgebied')


@void_no_crash()
@authenticate()
def error_updates(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, ErrorUpdates, change_error_updates)
        bot.sendMessage(chat_id, "Moeten error updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'error')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_error')


@void_no_crash()
@authenticate()
def hint_updates(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, HintUpdates, change_hint_updates)
        bot.sendMessage(chat_id, "Moeten hint updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'error')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_error')


###############################################################################
# conversation functions.                                                     #
#                                                                             #
###############################################################################


@void_no_crash()
@authenticate()
def conversation(bot, update):
    updater = Updates.get_updates()
    if not updater.has_bot():
        updater.add_bot(bot)
    updater.update()
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
    elif command == ErrorUpdates:
        add_error_listener_conversation(bot, update, state)
    elif command == NieuwsUpdates:
        add_nieuws_listener_conversation(bot, update, state)
    elif command == OpdrachtUpdates:
        add_opdracht_listener_conversation(bot, update, state)
    elif command == HintUpdates:
        add_hint_listener_conversation(bot, update, state)
    elif command == PhotoUpdates:
        pass  # TODO maak dit werkend
    elif command == SCOUTING_GROEP:
        pass  # TODO maak dit werkend
    elif command == SWITCH_REMINDERS:
        pass  # TODO maak dit werkend


@void_no_crash()
def deelgebied_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        if update.message.text in ['A', 'B', 'C', 'D', 'E', 'F', 'X', 'a', 'b', 'c', 'd', 'e', 'f', 'x']:
            state['deelgebied'] = update.message.text
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' moeten updates aan of uit staan voor dit deelgebied?')
            state.next_state()
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' Dat deelgebied ken ik niet. kies uit A, B, C, D, E, F of X.\n' +
                            ' of type /cancel om het comando te stoppen')
    if s == 1:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            state.done()
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' De updates zijn aan of uit gezet')
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' kies uit aan of uit.\n' +
                            ' of type /cancel om het comando te stoppen')


@void_no_crash()
def add_error_listener_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            state.done()
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' De Error updates zijn aan of uit gezet')
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' kies uit aan of uit.\n' +
                            ' of type /cancel om het commando te stoppen')


@void_no_crash()
def add_nieuws_listener_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            state.done()
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' De nieuws updates zijn aan of uit gezet')
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' kies uit aan of uit.\n' +
                            ' of type /cancel om het commando te stoppen')


@void_no_crash()
def add_opdracht_listener_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            state.done()
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' De opdracht updates zijn aan of uit gezet')
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' kies uit aan of uit.\n' +
                            ' of type /cancel om het commando te stoppen')


@void_no_crash()
def add_hint_listener_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            state.done()
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name + ' De hint updates zijn aan of uit gezet')
        else:
            bot.sendMessage(update.message.chat_id,
                            update.message.from_user.name +
                            ' kies uit aan of uit.\n' +
                            ' of type /cancel om het commando te stoppen')


###############################################################################
# callback functions.                                                         #
#                                                                             #
###############################################################################


@void_no_crash()
def change_dg_updates(state):
    updates = Updates.get_updates()
    if state['deelgebied'] in ['a', 'A']:
        updates.set_updates(state.chat_id, Updates.ALPHA, state['status'] == 'aan')
    elif state['deelgebied'] in ['b', 'B']:
        updates.set_updates(state.chat_id, Updates.BRAVO, state['status'] == 'aan')
    elif state['deelgebied'] in ['c', 'C']:
        updates.set_updates(state.chat_id, Updates.CHARLIE, state['status'] == 'aan')
    elif state['deelgebied'] in ['d', 'D']:
        updates.set_updates(state.chat_id, Updates.DELTA, state['status'] == 'aan')
    elif state['deelgebied'] in ['e', 'E']:
        updates.set_updates(state.chat_id, Updates.ECHO, state['status'] == 'aan')
    elif state['deelgebied'] in ['f', 'F']:
        updates.set_updates(state.chat_id, Updates.FOXTROT, state['status'] == 'aan')
    elif state['deelgebied'] in ['x', 'X']:
        updates.set_updates(state.chat_id, Updates.XRAY, state['status'] == 'aan')


@void_no_crash()
def change_error_updates(state):
    updates = Updates.get_updates()
    updates.set_updates(state.chat_id, Updates.ERROR, state['status'] == 'aan')


@void_no_crash()
def change_niews_updates(state):
    updates = Updates.get_updates()
    updates.set_updates(state.chat_id, Updates.NIEUWS, state['status'] == 'aan')


@void_no_crash()
def change_hints_updates(state):
    updates = Updates.get_updates()
    updates.set_updates(state.chat_id, Updates.HINTS, state['status'] == 'aan')