import telegram
from telegram.ext import Updater, MessageHandler, Filters
import settings
import Updates
from wrappers import void_no_crash, authenticate
from CommandHandlerWithHelp import CommandHandlerWithHelp
import authenticator


class MultipleConversationsError(Exception):
    pass


class NotCancelledError(Exception):
    pass

DEFAULT_KEYBOARD = [['/updates'], ['/check_updates'], ['/bug']]


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
    bot.sendMessage(update.message.chat_id, "er is in deze chat een error "
                                            "opgetreden:\n" + str(error))
    Updates.get_updates().error(error, "Updater")


def create_updater() -> Updater:
    updater = Updater(token=settings.Settings().bot_key)
    dp = updater.dispatcher
    help_updates = 'zet updates aan of uit voor diverse events'
    help_cancel = 'verlaat het huidige commando'
    help_crash = 'veroorzaak een test error'
    help_help = 'laat de helptext zien.'
    help_check_updates = 'kijk welke updates aan staan in deze chat.'
    help_start = 'start de bot'
    help_test = 'test of de bot online is.'
    help_bug = 'gebruik dit commando als iets te melden hebt over de app,  ' \
               'site of de bot. Of over een ander onderdeel van de hunt'
    help_phpsessid = 'HIER NIET AANKOMEN!!!!!!!!!!!! zet de phpsessid ' \
                     'cookie van jotihunt.net'
    help_set_url = 'HIER NIET AANKOMEN!! stel de url in voor ' \
                   'opdrachten/hunts/hints op jotihunt.net alleen nodig als ' \
                   'je in moet loggen om de link te openen.'
    chwh = set()
    chwh.add(CommandHandlerWithHelp('updates', updates, help_updates))
    chwh.add(CommandHandlerWithHelp('cancel', cancel, help_cancel))
    chwh.add(CommandHandlerWithHelp('crash', crash, help_crash))
    chwh.add(CommandHandlerWithHelp('help', help_command, help_help))
    chwh.add(CommandHandlerWithHelp('check_updates', check_updates,
                                    help_check_updates))
    chwh.add(CommandHandlerWithHelp('start', start, help_start))
    chwh.add(CommandHandlerWithHelp('test', test, help_test))
    chwh.add(CommandHandlerWithHelp('bug', bug, help_bug))
    chwh.add(CommandHandlerWithHelp('phpsessid', set_phpsessid,
                                    help_phpsessid))
    chwh.add(CommandHandlerWithHelp('set_url', set_url, help_set_url))
    chwh.add(MessageHandler([Filters.text], conversation))
    dp.add_handler(MessageHandler([Filters.status_update], on_new_user))
    for command_handler_with_help in chwh:
        dp.add_handler(command_handler_with_help)
    return updater


@void_no_crash()
@authenticate()
def set_phpsessid(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        state = State(bot, chat_id, user_id, phpsessid_conversation,
                      phpsessid_done)
        state['command'] = update.message.text
        state['from'] = update.message.from_user.name
        message = 'stap 1: login op jotihunt.net\n stap2: zoek uit hoe je ' \
                  'cookies van jothunt.net uitleest in je browser. \n stap ' \
                  '3: ga op zook naar de cookie met de naam PHPSESSID.\n  ' \
                  'stap 4: plak de waarde hier om de cookie te  verversen ' \
                  'van de bot.\n of /cancel om te stoppen'
        bot.sendMessage(chat_id, message,
                        reply_to_message_id=update.message.message_id)
    # TODO add a keyboard
        Updates.get_updates().botan.track(update.message, 'phpsessid')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit "
                                 "commando niet starten.\n"
                                 " type /cancel om het vorige commando te "
                                 "stoppen te stoppeny",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message,
                                          'incorrect_phpsessid')


@void_no_crash()
def on_new_user(bot, update):
    if update.message.new_chat_member:
        if update.message.new_chat_member.username:
            username = '@' + update.message.new_chat_member.username
        else:
            username = update.message.new_chat_member.first_name
        chatname = update.message.chat.title
        if authenticator.authenticate_chat(
                update.message.new_chat_member.id, update.message.chat_id,
                settings.Settings().SLEUTEL, username=username,
                chat_naam=chatname):
            bot.sendMessage(update.message.chat_id, 'welkom ' + username +
                            ' \n Je bent geregistreerd als gebruiker van de '
                            'RP Je kunt nu de bot gebruiken. /help')
        else:
            bot.sendMessage(update.message.chat_id, 'Welkom' + username +
                            'Deze chat is niet geverifieërd als chat van de '
                            'RP stuur een berichtje naar de HB om je te '
                            'registreren.')


###############################################################################
# command functions.                                                          #
#                                                                             #
###############################################################################
@void_no_crash()
def set_url(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        state = State(bot, chat_id, user_id, set_url_conversation,
                      set_url_done)
        state['command'] = update.message.text
        state['from'] = update.message.from_user.name
        bot.sendMessage(chat_id, "waar wil je de hunt voor instellen?\n "
                                 "hint/opdracht/nieuws",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=telegram.ReplyKeyboardMarkup([['hint'],
                                                                   ['opdracht'],
                                                                   ['nieuws'],
                                                                   ['/cancel']]))
        Updates.get_updates().botan.track(update.message, 'set_url')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit "
                                 "commando niet starten.\n"
                                 " type /cancel om het vorige commando te "
                                 "stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_set_url')


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
        keyboard = telegram.ReplyKeyboardMarkup([['app'], ['site'],
                                                 ['anders']])
        bot.sendMessage(chat_id, "Waar wil je een tip of een top voor "
                                 "sturen?\napp/bot/site/anders",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=keyboard)
        Updates.get_updates().botan.track(update.message, 'bug')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit "
                                 "commando niet starten.\n"
                                 " type /cancel om het vorige commando te "
                                 "stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_bug')


@void_no_crash()
@authenticate()
def test(bot, update):
    bot.sendMessage(update.message.chat_id, 'de bot is online')
    if update.message.chat_id > 0:
        url = Updates.get_updates().botan.shorten('http://google.com',
                                                  update.message.from_user.id)
    else:
        url = 'http://google.com'
    bot.sendMessage(update.message.chat_id, url)
    Updates.get_updates().botan.track(update.message, 'test')


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

Deze bot kan alleen gebruikt worden door de RP en daarom moet je eerst
geverifiërd worden.
Dat kan je op 2 manieren doen:
Je zet een berichtje in een groepsapp en dan wordt je automatisch geverifiërd.
Of je stuurt hier een berichtje en vraagt of de homebase je wil verifieren.
"""


@void_no_crash()
def start(bot, update):
    if update.message.chat_id > 0:
        keyboard = telegram.ReplyKeyboardMarkup(DEFAULT_KEYBOARD,
                                                one_time_keyboard=False)
        bot.sendMessage(update.message.chat_id, start_message,
                        reply_markup=keyboard)
    else:
        bot.sendMessage(update.message.chat_id, start_message)
    x = authenticate()
    x(lambda bot2, update2: print('authenticated:\n' + str(update.to_dict(
    ))))(bot, update)
    Updates.get_updates().botan.track(update.message, 'start')


@void_no_crash()
def help_command(bot, update):
    message = start_message + "\n\n"
    for commando in CommandHandlerWithHelp.helps:
        message += '/' + commando + ' - ' + CommandHandlerWithHelp.helps[
            commando] + '\n'
    bot.sendMessage(update.message.chat_id, message)
    Updates.get_updates().botan.track(update.message, 'help')


@void_no_crash()
@authenticate()
def crash(bot, update):
    bot.sendMessage(update.message.chat_id, 'we gaan de bot proberen te '
                                            'crashen')
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
        kb = telegram.ReplyKeyboardHide()
        if update.message.chat_id > 0:
            keyboard = DEFAULT_KEYBOARD
            kb = telegram.ReplyKeyboardMarkup(keyboard,
                                              one_time_keyboard=False,
                                              selective=True)
        bot.sendMessage(chat_id, "Er is geen commando actief.",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)
        Updates.get_updates().botan.track(update.message, 'incorrect_cancel')
    else:
        kb = telegram.ReplyKeyboardHide()
        if update.message.chat_id > 0:
            keyboard = DEFAULT_KEYBOARD
            kb = telegram.ReplyKeyboardMarkup(keyboard,
                                              one_time_keyboard=False,
                                              selective=True)
        bot.sendMessage(update.message.chat_id, "Het commando is gestopt.",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)
        Updates.get_updates().botan.track(update.message, 'cancel')


@void_no_crash()
@authenticate()
def updates(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    try:
        State(bot, chat_id, user_id, updates_conversation,
              change_updates)
        message = "Waarvoor moeten updates aan of uit staan?\n " \
                  "deelgebied, nieuws, hints, opdracht, error"
        keyboard = [['deelgebied'], ['nieuws'], ['hints'], ['opdracht'],
                    ['error'], ['/cancel']]
        kb = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                          selective=True)
        bot.sendMessage(chat_id, message,
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)
        Updates.get_updates().botan.track(update.message, 'update')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit "
                                 "commando niet starten.\n"
                                 " type /cancel om het vorige commando te "
                                 "stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message,
                                          'incorrect_update')


@void_no_crash()
@authenticate()
def sc_groep(bot, update):
    """

    :param bot:
    :param update:
    :return:
    """
    chat_id = update.message.chat_id
    try:
        # TODO implement this
        # TODO add a keyboard
        bot.sendMessage(chat_id, 'Deze functie doet nog niks')
        Updates.get_updates().botan.track(update.message, 'groep')
    except MultipleConversationsError:
        bot.sendMessage(chat_id, "Er is al een commando actief je kunt dit "
                                 "commando niet starten.\n"
                                 " type /cancel om het vorige commando te "
                                 "stoppen te stoppen",
                        reply_to_message_id=update.message.message_id)
        Updates.get_updates().botan.track(update.message, 'incorrect_groep')


###############################################################################
# conversation functions.                                                     #
#                                                                             #
###############################################################################

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
def set_url_conversation(bot, update, state):
    s = state.get_state()
    keyboard = None
    message = 'unexpected input!!'
    if s == 0:
        if update.message.text in ['hint', 'opdracht', 'nieuws']:
            message = 'Wat is de url zonder de id?\n bijv. ' \
                      'http://www.jotihunt.net/groep/opdracht.php?MID='
            state['soort'] = update.message.text
        else:
            message = 'kies uit hint, opdracht of nieuws. of /cancel om ' \
                      'terug te gaan.'
    if s == 1:
        state['url'] = update.message.text
        s.done()
        message = 'De url is aangepast voor ' + state['soort']
    if keyboard is not None:
        kb = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                          selective=True)
        bot.sendMessage(update.message.chat_id, message,
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)
    else:
        kb = telegram.ReplyKeyboardHide()
        if update.message.chat_id > 0:
            keyboard = DEFAULT_KEYBOARD
            kb = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=False,
                                              selective=True)
        bot.sendMessage(update.message.chat_id, message,
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)


@void_no_crash()
def updates_conversation(bot, update, state):
    s = state.get_state()
    message = 'unexpected input!!'
    keyboard = None
    if s == 0:
        if update.message.text == 'deelgebied':
            state['type'] = 'deelgebied'
            message = 'Voor welk deelgebied moeten de updates aan of uit ' \
                      'gezet worden?'
            l = []
            for dg in ['A', 'B', 'C', 'D', 'E', 'F', 'X', '/cancel']:
                l.append([dg])
            keyboard = l
            state.next_state()
        elif update.message.text in ['nieuws', 'hints', 'opdracht', 'error']:
            state['type'] = update.message.text
            message = 'moeten de updates voor {type} aan of uitgezet ' \
                      'worden?'.format(type=state['type'])
            keyboard = [['aan', 'uit', '/cancel']]
            state.next_state()
            state.next_state()
        else:
            message = 'Daar kan ik geen updates aan of uit voor zetten. '\
                      'waar moeten updates aan of uit voor staan? /cancel ' \
                      'om te stoppen.'
            l = []
            for dg in ['deelgebied', 'nieuws', 'hints', 'opdracht', 'error',
                       '/cancel']:
                l.append([dg])
            keyboard = l
    if s == 1:
        if update.message.text in ['A', 'B', 'C', 'D', 'E', 'F', 'X']:
            state['deelgebied'] = update.message.text
            message = 'Moeten de updates aan of uitgezet worden voor {' \
                      'deelgebied}?'
            message = message.format(deelgebied=update.message.text)
            keyboard = [['aan', 'uit', '/cancel']]
            state.next_state()
        else:
            message = 'Dat deelgebied ken ik niet. waar wil je updates aan ' \
                      'of uit voor zetten? /cancel om te stoppen.'
            l = []
            for dg in ['A', 'B', 'C', 'D', 'E', 'F', 'X', '/cancel']:
                l.append([dg])
            keyboard = l
    if s == 2:
        if update.message.text in ['aan', 'uit']:
            state['status'] = update.message.text
            message = 'De updates voor {type} zijn {status}gezet.'
            message = message.format(type=state['type'], status=state[
                'status'])
            botan_id = 'updates_{type}_{dg}_{status}'
            if state['type'] == 'deelgebied':
                dg = state['deelgebied']
            else:
                dg = ''
            botan_id = botan_id.format(type=state['type'], dg=dg,
                                       status=state['status'])
            state.done()
            Updates.get_updates().botan.track(update.message, botan_id)
        else:
            message = 'kies uit aan of uit'
            keyboard = [['aan', 'uit', '/cancel']]
    if keyboard is not None:
        kb = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                          selective=True)
        bot.sendMessage(update.message.chat_id, message,
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)
    else:
        kb = telegram.ReplyKeyboardHide()
        if update.message.chat_id > 0:
            keyboard = DEFAULT_KEYBOARD
            kb = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=False,
                                              selective=True)
        bot.sendMessage(update.message.chat_id, message,
                        reply_to_message_id=update.message.message_id,
                        reply_markup=kb)


@void_no_crash()
def phpsessid_conversation(bot, update, state):
    s = state.get_state()
    if s == 0:
        state['cookie'] = update.message.text
        state.done()

        bot.sendMessage(update.message.chat_id,
                        update.message.from_user.name + ' de cookie is '
                                                        'aangepast.')


@void_no_crash()
def bug_conversation(bot, update, state):
    s = state.get_state()
    if update.message.chat_id > 0:
        keyboard = telegram.ReplyKeyboardMarkup(DEFAULT_KEYBOARD)
    else:
        keyboard = telegram.ReplyKeyboardHide()
    if s == 0:
        state['about'] = update.message.text
        message = 'stuur nu je bug, feature, tip of top.'
        state.next_state()
    elif s == 1:
        state['message'] = update.message.text
        state.done()
        message = 'Je input is opgeslagen en doorgestuurd naar Bram Micky ' \
                  'en Mattijn (en evt. anderen).'
    else:
        message = ' dit is een fout in de bot graag aan mattijn laten weten,' \
                  'bug_conversation'
        Updates.get_updates().error(Exception(message), 'bug_conversation')
    bot.sendMessage(update.message.chat_id, message, reply_markup=keyboard)


###############################################################################
# callback functions.                                                         #
#                                                                             #
###############################################################################
@void_no_crash()
def change_updates(state):
    if state['type'] == 'deelgebied':
        change_dg_updates(state)
    elif state['type'] == 'opdracht':
        change_opdracht_updates(state)
    elif state['type'] == 'error':
        change_error_updates(state)
    elif state['type'] == 'nieuws':
        change_niews_updates(state)
    elif state['type'] == 'hints':
        change_hints_updates(state)


@void_no_crash()
def change_dg_updates(state):
    updates = Updates.get_updates()
    zet_aan = state['status'] in['aan', 'Aan']
    if state['deelgebied'] in ['a', 'A']:
        updates.set_updates(state.chat_id, Updates.ALPHA, zet_aan)
    elif state['deelgebied'] in ['b', 'B']:
        updates.set_updates(state.chat_id, Updates.BRAVO, zet_aan)
    elif state['deelgebied'] in ['c', 'C']:
        updates.set_updates(state.chat_id, Updates.CHARLIE, zet_aan)
    elif state['deelgebied'] in ['d', 'D']:
        updates.set_updates(state.chat_id, Updates.DELTA, zet_aan)
    elif state['deelgebied'] in ['e', 'E']:
        updates.set_updates(state.chat_id, Updates.ECHO, zet_aan)
    elif state['deelgebied'] in ['f', 'F']:
        updates.set_updates(state.chat_id, Updates.FOXTROT, zet_aan)
    elif state['deelgebied'] in ['x', 'X']:
        updates.set_updates(state.chat_id, Updates.XRAY, zet_aan)


@void_no_crash()
def change_opdracht_updates(state):
    updates = Updates.get_updates()
    zet_aan = state['status'] in ['aan', 'Aan']
    updates.set_updates(state.chat_id, Updates.OPDRACHTEN, zet_aan)


@void_no_crash()
def change_error_updates(state):
    updates = Updates.get_updates()
    zet_aan = state['status'] in ['aan', 'Aan']
    updates.set_updates(state.chat_id, Updates.ERROR, zet_aan)


@void_no_crash()
def change_niews_updates(state):
    updates = Updates.get_updates()
    zet_aan = state['status'] in ['aan', 'Aan']
    updates.set_updates(state.chat_id, Updates.NIEUWS, zet_aan)


@void_no_crash()
def change_hints_updates(state):
    updates = Updates.get_updates()
    zet_aan = state['status'] in ['aan', 'Aan']
    updates.set_updates(state.chat_id, Updates.HINTS, zet_aan)


@void_no_crash()
def bug_done(state):
    updates = Updates.get_updates()
    message = 'Er is bug gemeld.\n door: {van}\n aangeroepen met: '\
              '{command}\n het gaat over: {about}\n de text:\n {message}'
    message = message.format(van=state['from'], command=state['command'],
                             about=state['about'], message=state['message'])
    updates.error(Exception(message), 'bug_done')
    updates.bot.sendMessage(-158130982, message)


@void_no_crash()
def phpsessid_done(state):
    s = settings.Settings()
    u = Updates.get_updates()
    m = 'de phphsessid is aangepast van {old} naar {new}'
    u.error(Exception(m.format(old=str(s.phpsessid), new=str(state[
                                                                 'cookie']))),
            'php_sess_id')
    s.phpsessid = state['cookie']


@void_no_crash()
def set_url_done(state):
    s = settings.Settings()
    u = Updates.get_updates()
    m = 'de url voor {soort) is aangepast van {old} naar {new}'
    if state['soort'] == 'hint':
        m = m.format(soort='hints',
                     old=str(s.base_hint_url),
                     new=str(state['url']))
        s.base_hint_url = state['url']
    elif state['soort'] == 'opdracht':
        m = m.format(soort='opdrachten',
                     old=str(s.base_opdracht_url),
                     new=str(state['url']))
        s.base_opdracht_url = state['url']
    elif state['soort'] == 'nieuws':
        m = m.format(soort='nieuws',
                     old=str(s.base_nieuws_url),
                     new=str(state['url']))
        s.base_nieuws_url = state['url']
    u.error(Exception(m), 'set_url')
