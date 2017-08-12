from json import JSONDecodeError

from telegram import InlineKeyboardButton, Update, Message, InlineKeyboardMarkup, CallbackQuery, Bot, \
    ReplyKeyboardMarkup, KeyboardButton
from typing import List, Callable, Tuple, Union,  Dict
from threading import Lock

import Updates
from PythonApi.RPApi.Base import Api as RpApi

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler

import settings

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
            return "deze chat kan alleen gebruikt worden in prive chats", \
                   [InlineKeyboardButton("open chat", url="http://telegram.me/JotiHuntRP2_bot", callback_data='0')]
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

    def _set_up(self, update: Update, callback_query: str, rp_acc: Dict) -> Tuple[str,List[InlineKeyboardButton]]:
        if callback_query != '0':
            raise OldMenuException("verkeerde callback_querry !=0 ")
        self._get_next_buttons = self._main_menu
        if rp_acc.get("level", 25) >= 50:
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
            return 'Wat is je rol in de auto?',\
                   [InlineKeyboardButton('bestuurder', callback_data='1'),
                    InlineKeyboardButton('navigator', callback_data='2'),
                    InlineKeyboardButton('bijrijders', callback_data='3')
                    ]
        elif callback_query == '2':
            self._get_next_buttons = self._updates_menu
            return 'waar wil je updates aan of uit voor zetten?',\
                   [InlineKeyboardButton('check_updates', callback_data='1'),
                    InlineKeyboardButton('hints', callback_data='h'),
                    InlineKeyboardButton('opdrachten', callback_data='o'),
                    InlineKeyboardButton('nieuws', callback_data='n'),
                    InlineKeyboardButton('Alpha', callback_data='A'),
                    InlineKeyboardButton('Bravo', callback_data='B'),
                    InlineKeyboardButton('Charlie', callback_data='C'),
                    InlineKeyboardButton('Delta', callback_data='D'),
                    InlineKeyboardButton('Echo', callback_data='E'),
                    InlineKeyboardButton('Foxtrot', callback_data='F'),
                    InlineKeyboardButton('X-Ray', callback_data='X'),
                    InlineKeyboardButton('error', callback_data='e')
                    ]
        elif callback_query == '3':
            self._get_next_buttons = self._admin_menu
            return 'Dit menu is alleen beschikbaar voor admins. ',\
                   [InlineKeyboardButton('stel chats in', callback_data='1'),
                    InlineKeyboardButton('opdracht reminders uitzetten', callback_data='2'),
                    InlineKeyboardButton('opdracht reminders aanzetten', callback_data='3')
                    ]
        elif callback_query == '4':
            self._get_next_buttons = self._bug_menu
            return 'Waar wil je bug voor rapporteren?',\
                   [InlineKeyboardButton('app', callback_data='1'),
                    InlineKeyboardButton('bot', callback_data='2'),
                    InlineKeyboardButton('website', callback_data='3'),
                    InlineKeyboardButton('anders', callback_data='4'),
                    ]

    def _auto_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'Niet geimplenteerd', []

    def _updates_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        message = ''
        if callback_query == '1':
            for u in Updates.get_updates().check_updates(update.effective_chat.id):
                message += u + '\n'
            return message, []
        else:
            self._get_next_buttons = self._updates_aan_uit_menu
            message = 'updates voor ' + str(self.path[-1]) + ' aan of uit zetten.'
            return message, [
                InlineKeyboardButton('aan', callback_data='a'),
                InlineKeyboardButton('uit', callback_data='u')
            ]

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
        elif self.path[-2] == 'h':
            updates.set_updates(update.effective_chat.id, Updates.HINTS, zet_aan)
        elif self.path[-2] == 'n':
            updates.set_updates(update.effective_chat.id, Updates.NIEUWS, zet_aan)
        elif self.path[-2] == 'o':
            updates.set_updates(update.effective_chat.id, Updates.OPDRACHTEN, zet_aan)
        elif self.path[-2] == 'e':
            updates.set_updates(update.effective_chat.id, Updates.ERROR, zet_aan)
        return message, []

    def _admin_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'niet geimplenteerd', []

    def _bug_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'niet geimplenteerd', []

welcome_message = "welkom bij de bot voor de jotihunt bot!"


def start(bot: Bot, update: Update):
    message: Message = update.message
    with menus_lock:
        if message.chat_id not in menus:
            menus[message.chat_id] = Menu()
        else:
            # todo remove old keyboard and replace with the new one?
            pass
        menu = menus[message.chat_id]
    rp_acc = {'id': "21398373",
              'gebruikersnaam': "test",
              'level': 50}
    # todo rp_acc ophalen uit de api. None als de id niet gekoppeld is.
    text, buttons = menu.get_next_buttons(update, '0', rp_acc)
    keyboard = [[button] for button in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard= ReplyKeyboardMarkup([[KeyboardButton('/start')]
                                   , [KeyboardButton('verstuur hunter locatie', request_location=True)]])
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
    rp_acc = {'id': "21398373",
              'gebruikersnaam': "test",
              'level': 50}
    # todo rp_acc ophalen uit de api. None als de id niet gekoppeld is.
    try:
        message, buttons = menu.get_next_buttons(update, query.data, rp_acc)
    except OldMenuException as e:
        _, buttons = menu.get_next_buttons(update, '0', rp_acc)
        message = 'Je gebruikt een oud menu. Terug naar het hoofdmenu.'
    keyboard = [[button] for button in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text=message,
                          reply_markup=reply_markup,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def location_handler(bot, update):
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


def create_updater():
    updater = Updater(token=settings.Settings().bot_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(MessageHandler(Filters.location, location_handler))
    return updater