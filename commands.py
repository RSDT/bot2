from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import tokens
import logging
import time
import authenticator
from pythonApi.RPApi.Base import Api as RPApi
DeelgebiedUpdates, SWITCH_REMINDERS, BUG_REPORT, ErrorUpdates, SCOUTING_GROEP = range(4)


class MultipleConversationsError(Exception):
    pass


class NotCancelledError(Exception):
    pass


class Updates:
    _instance = None
    ALPHA, BRAVO, CHARLIE, DELTA, ECHO, FOXTROT, XRAY, PHOTOS, OPDRACHTEN, NIEUWS, ERROR = range(11)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Updates, cls).__new__(cls, *args)
        return cls._instance

    def __init__(self):
        self.bot = None
        self._A = set()
        self._B = set()
        self._C = set()
        self._D = set()
        self._E = set()
        self._F = set()
        self._X = set()
        self._photos = set()
        self._opdrachten = set()
        self._nieuws = set()
        self._error = set()
        self._last_update = 0
        self.lastA = None
        self.lastB = None
        self.lastC = None
        self.lastD = None
        self.lastE = None
        self.lastF = None
        self.lastX = None
        self.lastPhoto = None
        self.lastOpdracht = None
        self.lastNieuws = None
        self.lastStatus = None
        self.lastMail = None
        self.rp_api = RPApi.get_instance(tokens.rp_username, tokens.rp_pass)

    @void_no_crash()
    def update(self):
        if self.has_bot() and (self._last_update is None or abs(time.time() - self._last_update) > 60):
            pass
            self.update_vos_last()
            self.update_vos_status()
            self.update_nieuws()
            self.update_opdrachten()
            self.update_hint()
            self.update_foto_opdracht()
            self.update_mail()
            self.update_hunts()
        else:
            return

    @void_no_crash()
    def add_bot(self, bot):
        self.bot = bot

    def has_bot(self):
        return self.bot is not None

    @void_no_crash()
    def add_chat(self, chat_id, update_type):
        if update_type == self.ALPHA:
            self._A.add(chat_id)
        elif update_type == self.BRAVO:
            self._B.add(chat_id)
        elif update_type == self.CHARLIE:
            self._C.add(chat_id)
        elif update_type == self.DELTA:
            self._D.add(chat_id)
        elif update_type == self.ECHO:
            self._E.add(chat_id)
        elif update_type == self.FOXTROT:
            self._F.add(chat_id)
        elif update_type == self.XRAY:
            self._X.add(chat_id)
        elif update_type == self.PHOTOS:
            self._photos.add(chat_id)
        elif update_type == self.OPDRACHTEN:
            self._opdrachten.add(chat_id)
        elif update_type == self.NIEUWS:
            self._nieuws.add(chat_id)
        elif update_type == self.ERROR:
            self._error.add(chat_id)

    @void_no_crash()
    def remove_chat(self, chat_id, update_type):
        if update_type == self.ALPHA:
            self._A.remove(chat_id)
        elif update_type == self.BRAVO:
            self._B.remove(chat_id)
        elif update_type == self.CHARLIE:
            self._C.remove(chat_id)
        elif update_type == self.DELTA:
            self._D.remove(chat_id)
        elif update_type == self.ECHO:
            self._E.remove(chat_id)
        elif update_type == self.FOXTROT:
            self._F.remove(chat_id)
        elif update_type == self.XRAY:
            self._X.remove(chat_id)
        elif update_type == self.PHOTOS:
            self._photos.remove(chat_id)
        elif update_type == self.OPDRACHTEN:
            self._opdrachten.remove(chat_id)
        elif update_type == self.NIEUWS:
            self._nieuws.remove(chat_id)
        elif update_type == self.ERROR:
            self._error.add(chat_id)

    @void_no_crash()
    def set_updates(self, chat_id, dg, status):
        if status:
            self.add_chat(chat_id, dg)
        else:
            self.remove_chat(chat_id, dg)

    @void_no_crash()
    def update_vos_last(self):
        vosA = self.rp_api.vos('a')
        vosB = self.rp_api.vos('b')
        vosC = self.rp_api.vos('c')
        vosD = self.rp_api.vos('d')
        vosE = self.rp_api.vos('e')
        vosF = self.rp_api.vos('f')
        vosX = self.rp_api.vos('x')
        if self.lastA != vosA and self.has_bot():
            self.lastA = vosA
            for chat_id in self._A:
                if vosA['icon'] == '0':
                    self.bot.sendMessage(chat_id," Heeft een hint locatie verstuurd voor Alpha.")
                    self.bot.sendLocation(chat_id, lat=vosA['latitude'], lon=vosA['longitude'])
                elif vosA['icon'] == '1':
                    self.bot.sendMessage(chat_id," Heeft Vos Alpha gespot.")
                    self.bot.sendLocation(chat_id, lat=vosA['latitude'], lon=vosA['longitude'])
                elif vosA['icon'] == '2':
                    self.bot.sendMessage(chat_id," Heeft Vos Alpha gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosA['latitude'], lon=vosA['longitude'])
        if self.lastB != vosB and self.has_bot():
            self.lastB = vosB
            for chat_id in self._B:
                if vosB['icon'] == '0':
                    self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Bravo.")
                    self.bot.sendLocation(chat_id, lat=vosB['latitude'], lon=vosB['longitude'])
                elif vosB['icon'] == '1':
                    self.bot.sendMessage(chat_id, " Heeft Vos Bravo gespot.")
                    self.bot.sendLocation(chat_id, lat=vosB['latitude'], lon=vosB['longitude'])
                elif vosB['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Bravo gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosB['latitude'], lon=vosB['longitude'])
        if self.lastC != vosC and self.has_bot():
            self.lastC = vosC
            for chat_id in self._C:
                if vosC['icon'] == '0':
                    self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Charlie.")
                    self.bot.sendLocation(chat_id, lat=vosC['latitude'], lon=vosC['longitude'])
                elif vosC['icon'] == '1':
                    self.bot.sendMessage(chat_id, " Heeft Vos Charlie gespot.")
                    self.bot.sendLocation(chat_id, lat=vosC['latitude'], lon=vosC['longitude'])
                elif vosC['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Charlie gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosC['latitude'], lon=vosC['longitude'])
        if self.lastD != vosD and self.has_bot():
            self.lastD = vosD
            for chat_id in self._D:
                if vosD['icon'] == '0':
                    self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Delta.")
                    self.bot.sendLocation(chat_id, lat=vosD['latitude'], lon=vosD['longitude'])
                elif vosD['icon'] == '1':
                    self.bot.sendMessage(chat_id, " Heeft Vos Delta gespot.")
                    self.bot.sendLocation(chat_id, lat=vosD['latitude'], lon=vosD['longitude'])
                elif vosD['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Delta gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosD['latitude'], lon=vosD['longitude'])
        if self.lastE != vosE and self.has_bot():
            self.lastE = vosE
            for chat_id in self._E:
                if vosE['icon'] == '0':
                    self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Echo.")
                    self.bot.sendLocation(chat_id, lat=vosE['latitude'], lon=vosE['longitude'])
                elif vosE['icon'] == '1':
                    self.bot.sendMessage(chat_id, " Heeft Vos Echo gespot.")
                    self.bot.sendLocation(chat_id, lat=vosE['latitude'], lon=vosE['longitude'])
                elif vosE['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Echo gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosE['latitude'], lon=vosE['longitude'])
        if self.lastF != vosF and self.has_bot():
            self.lastF = vosF
            for chat_id in self._F:
                if vosF['icon'] == '0':
                    self.bot.sendMessage(chat_id," Heeft een hint locatie verstuurd voor Foxtrot.")
                    self.bot.sendLocation(chat_id, lat=vosF['latitude'], lon=vosF['longitude'])
                elif vosF['icon'] == '1':
                    self.bot.sendMessage(chat_id," Heeft Vos Foxtrot gespot.")
                    self.bot.sendLocation(chat_id, lat=vosF['latitude'], lon=vosF['longitude'])
                elif vosF['icon'] == '2':
                    self.bot.sendMessage(chat_id," Heeft Vos Foxtrot gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosF['latitude'], lon=vosF['longitude'])
        if self.lastX != vosX and self.has_bot():
            self.lastX = vosX
            for chat_id in self._X:
                if vosX['icon'] == '0':
                    self.bot.sendMessage(chat_id," Heeft een hint locatie verstuurd voor X-Ray.")
                    self.bot.sendLocation(chat_id, lat=vosX['latitude'], lon=vosX['longitude'])
                elif vosX['icon'] == '1':
                    self.bot.sendMessage(chat_id," Heeft Vos X-Ray gespot.")
                    self.bot.sendLocation(chat_id, lat=vosX['latitude'], lon=vosX['longitude'])
                elif vosX['icon'] == '2':
                    self.bot.sendMessage(chat_id," Heeft Vos X-Ray gehunt.")
                    self.bot.sendLocation(chat_id, lat=vosX['latitude'], lon=vosX['longitude'])

    @void_no_crash()
    def update_vos_status(self):
        pass

    @void_no_crash()
    def update_nieuws(self):
        pass

    @void_no_crash()
    def update_opdrachten(self):
        pass

    @void_no_crash()
    def update_hint(self):
        pass

    @void_no_crash()
    def update_foto_opdracht(self):
        pass

    @void_no_crash()
    def update_mail(self):
        pass

    @void_no_crash()
    def update_hunts(self):
        pass

    def error(self, e, func_name):
        for chat_id in self._error:
            if self.has_bot():
                self.bot.sendMessage(chat_id, "er is een error opgetreden:\n" + str(func_name)+'\n'+str(e))


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
        self.path = []
        self.state = 0
        self.callback = callback_on_done
        State.states[str(user_id) + str(chat_id)] = self

    @void_no_crash()
    def __setattr__(self, key, value):
        self._data[key] = value

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
    dp.add_error_handler(CommandHandler('error', error_updates))

    dp.add_handler(MessageHandler([Filters.text], conversation))
    return updater


def void_no_crash():
    def decorate(func):
        def call(*args, **kwargs):
            try:
                  func(*args, **kwargs)
            except Exception as e:
                logging.error(str(e))
                print(str(e))
                updates = Updates()
                updates.error(e, func.__name__)
        return call
    return decorate


@void_no_crash()
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
    elif command == ErrorUpdates:
        add_error_listener_conversation(bot, update, state)


###############################################################################
# conversation functions.                                                     #
#                                                                             #
###############################################################################
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
                            ' of type /cancel om het comando te stoppen')


###############################################################################
# command functions.                                                          #
#                                                                             #
###############################################################################
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
    else:
        bot.sendMessage(chat_id, "Het commando is gestopt.", reply_to_message_id=update.message.message_id)

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
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)


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
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit commando niet starten.\n"
                                 " type /cancel om het vorige comando te stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)








###############################################################################
# callback functions.                                                         #
#                                                                             #
###############################################################################
@void_no_crash()
def change_dg_updates(state):
    updates = Updates()
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
    updates = Updates()
    updates.set_updates(state.chat_id, Updates.ERROR, state['status'] == 'aan')