from telegram.ext import Updater, MessageHandler, Filters
import tokens
import Updates
from wrappers import void_no_crash, authenticate
from CommandHandlerWithHelp import CommandHandlerWithHelp
import authenticator


class MultipleConversationsError(Exception):
    pass


class NotCancelledError(Exception):
    pass


class State:
    states = dict()

    def __init__(self, bot, chat_id, user_id, responder, callback_on_done):
        """

        :raises MultipleConversationsError als de gebruiker al in een chat zit.
        """
        if (str(user_id) + str(chat_id)) in State.states:
            raise MultipleConversationsError()
        self._data = dict()
        self.chat_id = chat_id
        self.bot = bot
        self.user_id = user_id
        self.responer = responder
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
    dp.add_handler(CommandHandlerWithHelp('help', help_command, 'laat de helptext zien.'))
    dp.add_handler(CommandHandlerWithHelp('check_updates', check_updates, 'kijk welke updates aan staan in deze chat.'))
    dp.add_handler(CommandHandlerWithHelp('start', start, 'start de bot'))
    dp.add_handler(CommandHandlerWithHelp('nieuws', nieuws_updates, 'zet nieuws updates aan of uit'))
    dp.add_handler(CommandHandlerWithHelp('test', test, 'test of de bot online is.'))
    dp.add_handler(CommandHandlerWithHelp('opdrachten', opdrachten, 'zet opdracht updates aan of uit.'))
    dp.add_handler(CommandHandlerWithHelp('hints', hint_updates, 'zet hint updates aan of uit.'))
    dp.add_handler(CommandHandlerWithHelp('fotos', photo_updates, 'zet foto updates aan of uit.'))
    dp.add_handler(CommandHandlerWithHelp('bug', bug, 'gebruik dit commando als iets te melden hebt over de app,  site ofde bot. Of over een ander onderdeel van de hunt'))
    dp.add_handler(MessageHandler([Filters.text], conversation))
    dp.add_handler(MessageHandler([Filters.status_update], on_new_user))
    return updater


def on_new_user(bot, update):
    if update.message.new_chat_member:
        if update.message.new_chat_member.username:
            username = '@' + update.message.new_chat_member.username
        else:
            username = update.message.new_chat_member.first_name
        chatname = update.message.chat.title
        if authenticator.authenticate_chat(update.message.new_chat_member.id, update.message.chat_id, tokens.SLEUTEL,
                                           username=username, chat_naam=chatname):
            bot.sendMessage(update.message.chat_id, 'welkom ' + username +
                            ' \n Je bent geregistreerd als gebruiker van de RP Je kunt nu de bot gebruiken. /help')
        else:
            bot.sendMessage(update.message.chat_id, 'Welkom' + username +
                            'Deze chat is niet geverifieërd als chat van de RP stuur een berichtje naar de HB om je te registreren.')


###############################################################################
# command functions.                                                          #
#                                                                             #
###############################################################################
@void_no_crash()
def bug(bot, update):
    """

                :param bot:
                :param update:
                :return:
                """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        state = State(bot, chat_id, user_id, bug_conversation, bug_done)
        state['command'] = update.message.text
        state['from'] = update.message.from_user.name
        bot.sendMessage(chat_id, "Waar wil je een tip of een top voor sturen?\napp/bot/site/anders",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'bug')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_bug')


@void_no_crash()
@authenticate()
def opdrachten(bot, update):
    """

            :param bot:
            :param update:
            :return:
            """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, add_opdracht_listener_conversation, change_niews_updates)
        bot.sendMessage(chat_id, "Moeten opdracht updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'opdracht_update')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_opdracht_update')


@void_no_crash()
@authenticate()
def test(bot, update):
    bot.sendMessage(update.message.chat_id, 'de bot is online')
    url = Updates.get_updates().botan.shorten('google', update.message.from_user.id)
    bot.sendMessage(update.message.chat_id, url)
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
        State(bot, chat_id, user_id, add_nieuws_listener_conversation, change_niews_updates)
        bot.sendMessage(chat_id, "Moeten nieuws updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'nieuws_update')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
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
    x = authenticate()
    x(lambda bot2, update2: print('authenticated:\n' + str(update.to_dict())))(bot, update)
    Updates.get_updates().botan.track(update.message, 'start')


@void_no_crash()
def help_command(bot, update):
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
        State(bot, chat_id, user_id, deelgebied_conversation, change_dg_updates)
        bot.sendMessage(chat_id, "Voor welk deelgebied moeten updates aan of uit staan?\nA, B, C, D, E, F, X",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'deelgebied')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
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
        State(bot, chat_id, user_id, add_error_listener_conversation, change_error_updates)
        bot.sendMessage(chat_id, "Moeten error updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'error')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
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
        State(bot, chat_id, user_id, add_hint_listener_conversation, change_hints_updates)
        bot.sendMessage(chat_id, "Moeten hint updates aan of uit staan?\naan/uit",
                        reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'hints')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_hints')


@void_no_crash()
@authenticate()
def photo_updates(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        # State(bot, chat_id, user_id, PhotoUpdates, change_opdracht_updates)
        # TODO implement this
        # bot.sendMessage(chat_id, "Moeten hint updates aan of uit staan?\naan/uit",
        #                reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        bot.sendMessage(chat_id, 'Deze functie doet nog niks')
        Updates.get_updates().botan.track(update.message, 'fotos')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_fotos')


@void_no_crash()
@authenticate()
def sc_groep(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        # State(bot, chat_id, user_id, PhotoUpdates, change_opdracht_updates)
        # TODO implement this
        # bot.sendMessage(chat_id, "Moeten hint updates aan of uit staan?\naan/uit",
        #                reply_to_message_id=update.message.message_id)  # TODO add a keyboard
        bot.sendMessage(chat_id, 'Deze functie doet nog niks')
        Updates.get_updates().botan.track(update.message, 'groep')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige commando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_groep')


########################################################################################################################
# conversation functions.                                                                                              #
#                                                                                                                      #
########################################################################################################################

@void_no_crash()
def conversation(bot, update):
    """

    :rtype: None
    :param bot:
    :param update:
    :return:
    """
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
    state.responer(bot, update, state)
    return


@void_no_crash()
def deelgebied_conversation(bot, update, state):
    """

    :param bot:
    :param update:
    :param state:
    """
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
                            ' of type /cancel om het commando te stoppen')
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
                            ' of type /cancel om het commando te stoppen')


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


@void_no_crash()
def bug_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        state['about'] = update.message.text
        bot.sendMessage(update.message.chat_id, 'stuur nu je bug, feature, tip of top.')
        state.next_state()
    if s == 1:
        state['message'] = update.message.text
        state.done()
        bot.sendMessage(update.message.chat_id,
                        'Je input is opgeslagen en doorgestuurd naar Bram Micky en Mattijn (en evt. anderen).')
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


@void_no_crash()
def bug_done(state):
    bot = Updates.get_updates().bot
    bot.sendMessage(-158130982, 'Er is bug gemeld.\n' +
                    'door: ' + state['from'] + '\n' +
                    'aangeroepen met: ' + state['command'] + '\n' +
                    'het gaat over: ' + state['about'] + '\n' +
                    'de text:\n' + state['message'])
