import os
import pickle
from json import JSONDecodeError

import sys
from telegram import InlineKeyboardButton, Update, Message, InlineKeyboardMarkup, CallbackQuery, Bot, \
    ReplyKeyboardMarkup, KeyboardButton, User, Chat
from typing import List, Callable, Tuple, Union,  Dict
from threading import Lock

import Updates
import reminders
from IdsObserver import IdsObserver
from PythonApi.RPApi.Base import Api as RpApi

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler

import settings

STARTUPFILE = 'startup.jhu'

menus = dict()
menus_lock = Lock()


class OldMenuException(Exception):
    pass


class Menu:
    def __init__(self):
        self._get_next_buttons: Callable[[Menu, Update, str, Dict], List[InlineKeyboardButton]] = self._set_up
        self.path = []

    def get_next_buttons(self, update: Update, callback_query: str='0', rp_acc: Union[None, Dict]=None):
        chat_id: Message = update.effective_chat.id
        if chat_id < 0:
            if callback_query == '0':
                return "deze chat kan alleen gebruikt worden in prive chats of om te controleren waar updates voor " \
                   "aanstaan in deze chat", \
                   [InlineKeyboardButton("open prive chat",  url="http://telegram.me/JotiHuntRP2_bot",
                                         callback_data='0'),
                    InlineKeyboardButton('check updates', callback_data='1')]
            else:
                l = lambda message, buttons: (message, [InlineKeyboardButton('terug naar hoofdmenu', callback_data='0')])
                return l(*self._updates_menu(update, '1', rp_acc))
        if rp_acc is None:
            return "Dit account is nog niet gelinked aan de RP database. " \
                   "Vraag aan de HB om dit te doen en klik daarna op start.", \
                   [InlineKeyboardButton('start', callback_data='0')]
        self.path.append(callback_query)
        if callback_query == '0':
            self._get_next_buttons = self._set_up
            self.path.clear()
        text, buttons = self._get_next_buttons(update, callback_query, rp_acc)
        if callback_query != '0':
            buttons.append(InlineKeyboardButton('terug naar hoofdmenu', callback_data='0'))
        return text, buttons

    def _set_up(self, update: Update, callback_query: str, rp_acc: Dict) -> Tuple[str, List[InlineKeyboardButton]]:
        if callback_query != '0':
            raise OldMenuException("verkeerde callback_querry !=0 ")
        self._get_next_buttons = self._main_menu
        if int(rp_acc.get("toegangslvl", 25)) >= 50:
            return 'Welkom Bij de bot. Wat wil je doen?',\
                   [InlineKeyboardButton('auto', callback_data='1'),
                    InlineKeyboardButton('updates', callback_data='2'),
                    InlineKeyboardButton('admin controls', callback_data='3'),
                    InlineKeyboardButton('report a bug', callback_data='4'),
                    ]
        else:
            return 'Welkom Bij de bot. Wat wil je doen?',\
                   [InlineKeyboardButton('auto', callback_data='1'),
                    InlineKeyboardButton('updates', callback_data='2'),
                    InlineKeyboardButton('report a bug', callback_data='4'),
                    ]

    def _main_menu(self, update:Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        if callback_query == '1':
            self._get_next_buttons = self._auto_menu
            not_in_auto = True
            if not_in_auto:
                return 'Wat is je rol in de auto?',\
                       [InlineKeyboardButton('bestuurder', callback_data='m_1'),
                        InlineKeyboardButton('navigator', callback_data='m_2'),
                        InlineKeyboardButton('bijrijders', callback_data='m_3')
                        ]
            else:
                bestuurder = False
                navigator = True
                if not bestuurder:
                    buttons = [InlineKeyboardButton('stap uit auto', callback_data='b_4')]
                else:
                    buttons = [InlineKeyboardButton('stap uit auto en verwijder de auto uit de db')]
                if bestuurder or navigator:
                    buttons.append(InlineKeyboardButton('verander de taak', callback_data='b_5'))
                return 'je zit al in een auto, wat wil je down?', buttons

        elif callback_query == '2':
            self._get_next_buttons = self._updates_menu
            return 'waar wil je updates aan of uit voor zetten?',\
                   [InlineKeyboardButton('check_updates', callback_data='u_1'),
                    InlineKeyboardButton('hints', callback_data='hints'),
                    InlineKeyboardButton('opdrachten', callback_data='opdracht'),
                    InlineKeyboardButton('nieuws', callback_data='nieuws'),
                    InlineKeyboardButton('Alpha', callback_data='A'),
                    InlineKeyboardButton('Bravo', callback_data='B'),
                    InlineKeyboardButton('Charlie', callback_data='C'),
                    InlineKeyboardButton('Delta', callback_data='D'),
                    InlineKeyboardButton('Echo', callback_data='E'),
                    InlineKeyboardButton('Foxtrot', callback_data='F'),
                    InlineKeyboardButton('X-Ray', callback_data='X'),
                    InlineKeyboardButton('error', callback_data='error')
                    ]
        elif callback_query == '3':
            self._get_next_buttons = self._admin_menu
            return 'Dit menu is alleen beschikbaar voor admins. ',\
                   [# InlineKeyboardButton('stel chats in', callback_data='a_1'),
                    InlineKeyboardButton('updates voor een groepsapp uitzetten', callback_data='uit'),
                    InlineKeyboardButton('updates voor een groepsapp aanzetten', callback_data='aan'),
                    InlineKeyboardButton('opdracht reminders uitzetten', callback_data='reminder_uit'),
                    InlineKeyboardButton('opdracht reminders aanzetten', callback_data='reminder_aan'),
                    InlineKeyboardButton('gebruiker buffer naar de site sturen', callback_data='a_4'),
                    InlineKeyboardButton('gebruiker uit buffer verwijderen', callback_data='a_5')
                    ]
        elif callback_query == '4':
            self._get_next_buttons = self._bug_menu
            return 'Waar wil je bug voor rapporteren?',\
                   [InlineKeyboardButton('app', callback_data='app'),
                    InlineKeyboardButton('bot', callback_data='bot'),
                    InlineKeyboardButton('website', callback_data='site'),
                    InlineKeyboardButton('anders', callback_data='anders'),
                    ]
        else:
            return 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   'main_menu, ' + str(callback_query), []

    def _auto_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'Niet geimplenteerd', []

    def _updates_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        message = ''
        if callback_query == 'u_1':
            for u in Updates.get_updates().check_updates(update.effective_chat.id):
                message += u + '\n'
            return message, []
        elif callback_query in ['hints', 'opdracht', 'nieuws', 'error', 'A', 'B', 'C', 'D', 'E', 'F', 'X']:
            self._get_next_buttons = self._updates_aan_uit_menu
            message = 'updates voor ' + str(self.path[-1]) + ' aan of uit zetten.'
            return message, [
                InlineKeyboardButton('aan', callback_data='a'),
                InlineKeyboardButton('uit', callback_data='u')
            ]
        else:
            return 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   'updates_menu, ' + str(callback_query), []

    def _updates_aan_uit_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        updates = Updates.get_updates()
        message = ''
        zet_aan = callback_query == 'a'
        if zet_aan:
            message = 'updates voor ' + str(self.path[-2]) + ' zijn aangezet.'
        else:
            message = 'updates voor ' + str(self.path[-2]) + ' zijn uitgezet.'
        if self.path[-2] == 'A':
            updates.set_updates(update.effective_chat.id, Updates.ALPHA, zet_aan)
        elif self.path[-2] == 'B':
            updates.set_updates(update.effective_chat.id, Updates.BRAVO, zet_aan)
        elif self.path[-2] == 'C':
            updates.set_updates(update.effective_chat.id, Updates.CHARLIE, zet_aan)
        elif self.path[-2] == 'D':
            updates.set_updates(update.effective_chat.id, Updates.DELTA, zet_aan)
        elif self.path[-2] == 'E':
            updates.set_updates(update.effective_chat.id, Updates.ECHO, zet_aan)
        elif self.path[-2] == 'F':
            updates.set_updates(update.effective_chat.id, Updates.FOXTROT, zet_aan)
        elif self.path[-2] == 'X':
            updates.set_updates(update.effective_chat.id, Updates.XRAY, zet_aan)
        elif self.path[-2] == 'hints':
            updates.set_updates(update.effective_chat.id, Updates.HINTS, zet_aan)
        elif self.path[-2] == 'nieuws':
            updates.set_updates(update.effective_chat.id, Updates.NIEUWS, zet_aan)
        elif self.path[-2] == 'opdracht':
            updates.set_updates(update.effective_chat.id, Updates.OPDRACHTEN, zet_aan)
        elif self.path[-2] == 'error':
            updates.set_updates(update.effective_chat.id, Updates.ERROR, zet_aan)
        else:
            message = 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   '_updates_aan_uit_menu, ' + str(callback_query)
        return message, []

    def _admin_menu_updates_group_2(self, update: Update, callback_query: str, rp_acc) -> Tuple[
        str, List[InlineKeyboardButton]]:
        updates = Updates.get_updates()
        chat_id = self.path[-2]
        update_type = self.path[-1]
        zet_aan = self.path[-3] == 'aan'

        if zet_aan:
            message = 'updates voor ' + str(update_type) + ' zijn aangezet.'
        else:
            message = 'updates voor ' + str(update_type) + ' zijn uitgezet.'
        if update_type == 'A':
            updates.set_updates(chat_id, Updates.ALPHA, zet_aan)
        elif update_type == 'B':
            updates.set_updates(chat_id, Updates.BRAVO, zet_aan)
        elif update_type == 'C':
            updates.set_updates(chat_id, Updates.CHARLIE, zet_aan)
        elif update_type == 'D':
            updates.set_updates(chat_id, Updates.DELTA, zet_aan)
        elif update_type == 'E':
            updates.set_updates(chat_id, Updates.ECHO, zet_aan)
        elif update_type == 'F':
            updates.set_updates(chat_id, Updates.FOXTROT, zet_aan)
        elif update_type == 'X':
            updates.set_updates(chat_id, Updates.XRAY, zet_aan)
        elif update_type == 'hints':
            updates.set_updates(chat_id, Updates.HINTS, zet_aan)
        elif update_type == 'nieuws':
            updates.set_updates(chat_id, Updates.NIEUWS, zet_aan)
        elif update_type == 'opdracht':
            updates.set_updates(chat_id, Updates.OPDRACHTEN, zet_aan)
        elif update_type == 'error':
            updates.set_updates(chat_id, Updates.ERROR, zet_aan)
        else:
            message = 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   '_admin_menu_updates_group_2, ' + str(callback_query) + ', ' + str(self.path)
        return message, []

    def _admin_menu_updates_group_1(self, update: Update, callback_query: str, rp_acc) -> Tuple[str, List[InlineKeyboardButton]]:
        self._get_next_buttons = self._admin_menu_updates_group_2
        if self.path[1] in ('uit', 'aan'):
            return 'Waarvoor moeten updates aan of uitgezet worden?', [
                        InlineKeyboardButton('hints', callback_data='hints'),
                        InlineKeyboardButton('opdrachten', callback_data='opdracht'),
                        InlineKeyboardButton('nieuws', callback_data='nieuws'),
                        InlineKeyboardButton('Alpha', callback_data='A'),
                        InlineKeyboardButton('Bravo', callback_data='B'),
                        InlineKeyboardButton('Charlie', callback_data='C'),
                        InlineKeyboardButton('Delta', callback_data='D'),
                        InlineKeyboardButton('Echo', callback_data='E'),
                        InlineKeyboardButton('Foxtrot', callback_data='F'),
                        InlineKeyboardButton('X-Ray', callback_data='X'),
                        InlineKeyboardButton('error', callback_data='error')
                                                                   ]
        else:
            return 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   '_admin_menu_updates_group_1, ' + str(callback_query) + ', ' + str(self.path), []

    def _admin_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        if callback_query == 'a_1':
            return 'niet geimplenteerd', []
        elif callback_query in ['uit', 'aan']:
            chats = IdsObserver()
            buttons = []
            self._get_next_buttons = self._admin_menu_updates_group_1
            for tid in chats.group_chats:
                buttons.append(InlineKeyboardButton(chats.group_chats[tid], callback_data=str(tid)))
            return 'voor welke chat wil je uupdates aan of uitzetten?', buttons
        elif callback_query == 'a_4':
            users = IdsObserver()
            users.send_users_buffer()
            return 'gebruikers zijn naar de site gestuurd', []
        elif callback_query == 'a_5':
            users = IdsObserver()
            with users.users_lock:
                buttons = []
                for user_id in users.user_buffer:
                    buttons.append(InlineKeyboardButton(users.getName(user_id), callback_data=str(user_id)))
            self._get_next_buttons = self._admin_menu_remove_user
            return 'welke gebruiker moet worden verwijder uit de buffer?', buttons
        elif callback_query in ['reminder_uit', 'reminder_aan']:
            self._get_next_buttons = self._reminder_menu
            updates = Updates.get_updates()
            with updates._reminders_lock:
                buttons = []
                for opdracht_id in updates.reminders:
                    reminder: reminders.Reminder = updates.reminders[opdracht_id]
                    message = reminder.titel
                    if reminders.check_reminder(opdracht_id):
                        message += ' ;staat nu aan'
                    else:
                        message += ' ;staat nu uit'
                    buttons.append(InlineKeyboardButton(message, callback_data=opdracht_id))
            return 'waar wil je reminders aan of uit voor zetten?', buttons
        else:
            return 'error, waarschijnlijk heb je meerdere knoppen in het zelfde menu ingedrukt.\n' \
                   'admin_menu, ' + str(callback_query), []

    def _reminder_menu(self, update, callback_querry, rp_acc):
        zet_aan = self.path[-2] == 'reminder_aan'
        opdracht_id = self.path[-1]
        if zet_aan:
            message = 'reminders aangezet'
            reminders.reset_reminder(opdracht_id)
        else:
            message = 'reminders uitgezet'
            reminders.done(opdracht_id)
        return message, []

    def _admin_menu_remove_user(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        users = IdsObserver()
        with users.users_lock:
            del users.user_buffer[int(callback_query)]
        return 'user verwijderd uit de buffer', []

    def _bug_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        updates = Updates.get_updates()
        message = 'Er is bug gemeld.\n door: {van}\n aangeroepen met: ' \
                  '{command}\n het gaat over: {about}\n de text:\n {message}'
        message = message.format(van=update.effective_user.name, command='bug menu',
                                 about=self.path[-1], message='{message}')
        updates.error(Exception(message), 'bug_done')
        return 'er is gemeld dat je een bug hebt', []

welcome_message = "welkom bij de bot voor de jotihunt van de RP!"


def start(bot: Bot, update: Update):
    users_handler(bot, update)
    message: Message = update.message
    with menus_lock:
        if message.chat_id not in menus:
            menus[message.chat_id] = Menu()
        else:
            # todo remove old keyboard and replace with the new one?
            pass
        menu = menus[message.chat_id]
    api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
    response = api.get_telegram_link(update.effective_user.id)
    rp_acc = response.data
    if rp_acc is None:
        user: User = update.effective_user
        api.send_telegram_user(user.id, user.first_name, user.last_name, user.username)
        bot.send_message(update.effective_chat.id, 'Je telegram account is nog niet gelinkt.'
                                                   'Vraag aan de homebase of ze dat willen doen. '
                                                   'En zeg daarna /start.',
                         reply_to_message_id=update.effective_message.message_id)
    text, buttons = menu.get_next_buttons(update, '0', rp_acc)
    keyboard = [[button] for button in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.effective_chat.type == Chat.PRIVATE:
        keyboard = ReplyKeyboardMarkup([[KeyboardButton('/start met het laten zien van het menu')]
                                   , [KeyboardButton('verstuur hunter locatie', request_location=True)]])
    else:
        keyboard = ReplyKeyboardMarkup([])
    bot.send_message(update.effective_chat.id, welcome_message, reply_markup=keyboard)
    message.reply_text(text, reply_markup=reply_markup)


def handle_callback(bot, update):
    with menus_lock:
        if update.effective_chat.id not in menus:
            menus[update.effective_chat.id] = Menu()
        else:
            # todo remove old keyboard and replace with the new one?
            pass
        menu = menus[update.effective_chat.id]
    query: CallbackQuery = update.callback_query
    api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
    response = api.get_telegram_link(update.effective_user.id)
    rp_acc = response.data
    try:
        message, buttons = menu.get_next_buttons(update, query.data, rp_acc)
    except OldMenuException as e:
        _, buttons = menu.get_next_buttons(update, '0', rp_acc)
        message = 'Je gebruikt een oud menu. Terug naar het hoofdmenu.'
    keyboard = [[button] for button in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text=message+'.',
                          reply_markup=reply_markup,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def location_handler(bot, update):
    api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
    response = api.get_telegram_link(update.effective_user.id)
    rp_acc = response.data
    if rp_acc is None:
        user: User = update.effective_user
        api.send_telegram_user(user.id, user.first_name, user.last_name, user.username)
        bot.send_message(update.effective_chat.id, 'Je telegram account is nog niet gelinkt.'
                                                   ' vraag aan de homebase of ze dat willen doen.',
                         reply_to_message_id=update.effective_message.message_id)
    if update.effective_message.reply_to_message.text == welcome_message:
        api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
        try:
            api.send_hunter_location(update.effective_message.location.latitude, update.effective_message.location.longitude, hunternaam=update.effective_message.from_user.name)
        except JSONDecodeError as e:
            bot.send_message(update.effective_chat.id, 'locatie verzonden', reply_to_message_id=update.effective_message.message_id)
        except Exception as e:
            bot.send_message(update.effective_chat.id, 'error: locatie waarschijnlijk niet verzonden', reply_to_message_id=update.effective_message.id)
            raise e
        else:
            bot.send_message(update.effective_chat.id, 'locatie verzonden',
                             reply_to_message_id=update.effective_message.message_id)


def users_handler(bot, update):
    users = IdsObserver()
    if update.effective_user is not None:
        user: User = update.effective_user
        users.add_user_to_buffer(user.id, user.first_name, user.last_name, user.username)
    if update.effective_chat is not None:
        chat: Chat = update.effective_chat
        users.add_group_chat(chat.type, chat.id, chat.title)


def stop(updater: Updater):
    def handler(bot, update):
        api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
        response = api.get_telegram_link(update.effective_user.id)
        rp_acc = response.data
        if rp_acc is None:
            bot.send_message(update.effective_chat.id, 'Je telegram account is nog niet gelinkt.'
                                                       ' vraag aan de homebase of ze dat willen doen.',
                             reply_to_message_id=update.effective_message.message_id)
            return
        if int(rp_acc['toegangslvl']) < 75 and int(update.effective_user.id)\
                != 19594180:
            bot.send_message(update.effective_chat.id, 'Je bent niet gemachtigd om dit commando uit te voeren',
                             reply_to_message_id=update.effective_message.message_id)
            return

        bot.send_message(update.effective_chat.id, "bot gaat stoppen.")
        try:
            updates: Updates = Updates.get_updates()
            updates.to_all('de bot gaat afsluiten')
            updates.exit()
            updates.save()
            with open(STARTUPFILE, 'wb') as file:
                pickle.dump({'command': 'stop'}, file)
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(e)
            raise e
        # updater.is_idle = False
    return handler


def save(bot, update):
    updates: Updates = Updates.get_updates()
    updates.save()
    updates.send_message(update.effective_chat.id, 'huidige staat opgeslagen')

def restart(bot, update):
    api = RpApi.get_instance(settings.Settings().rp_username, settings.Settings().rp_pass)
    response = api.get_telegram_link(update.effective_user.id)
    rp_acc = response.data
    if rp_acc is None:
        bot.send_message(update.effective_chat.id, 'Je telegram account is nog niet gelinkt.'
                                                   ' vraag aan de homebase of ze dat willen doen.',
                         reply_to_message_id=update.effective_message.message_id)
        return
    if int(rp_acc['toegangslvl']) < 75 and int(update.effective_user.id) != 19594180:
        bot.send_message(update.effective_chat.id, 'Je bent niet gemachtigd om dit commando uit te voeren',
                         reply_to_message_id=update.effective_message.message_id)
        return
    bot.send_message(update.effective_chat.id, "bot gaat herstarten.")
    try:
        updates: Updates = Updates.get_updates()
        updates.to_all('de bot gaat herstarten')
        updates.exit()
        updates.save()
        with open(STARTUPFILE, 'wb') as file:
            pickle.dump({'command': 'restart'}, file)
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(e)
        raise e


def create_updater():
    updater = Updater(token=settings.Settings().bot_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('restart', restart))
    dp.add_handler(CommandHandler('save', save))
    dp.add_handler(CommandHandler('stop', stop(updater)))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(MessageHandler(Filters.location, location_handler))
    dp.add_handler(MessageHandler(Filters.all, users_handler))

    return updater
