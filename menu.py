from telegram import InlineKeyboardButton, Update, Message, InlineKeyboardMarkup, CallbackQuery, Bot, \
    ReplyKeyboardMarkup, KeyboardButton
from typing import List, Callable, Tuple, Union,  Dict
from threading import Lock

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

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
        self.path.append(InlineKeyboardButton('start', callback_data='0'))
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
        if callback_query not in ['1', '2', '3', '4']:
           raise Exception("callback not in 1,2,3,4")
        elif callback_query == '1':
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
                    InlineKeyboardButton('hints', callback_data='2'),
                    InlineKeyboardButton('opdrachten', callback_data='3'),
                    InlineKeyboardButton('nieuws', callback_data='4'),
                    InlineKeyboardButton('Alpha', callback_data='5'),
                    InlineKeyboardButton('Bravo', callback_data='6'),
                    InlineKeyboardButton('Charlie', callback_data='7'),
                    InlineKeyboardButton('Delta', callback_data='8'),
                    InlineKeyboardButton('Echo', callback_data='9'),
                    InlineKeyboardButton('Foxtrot', callback_data='10'),
                    InlineKeyboardButton('X-Ray', callback_data='11')
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
        # todo implement this
        return 'niet geimplenteerd', []

    def _admin_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'niet geimplenteerd', []

    def _bug_menu(self, update: Update, callback_query: str, rp_acc)->Tuple[str, List[InlineKeyboardButton]]:
        # todo implement this
        return 'niet geimplenteerd', []


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
              'level': 25}
    # todo rp_acc ophalen uit de api. None als de id niet gekoppeld is.
    text, buttons = menu.get_next_buttons(update, '0', rp_acc)
    keyboard = [[button] for button in buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(update.effective_chat.id, "welkom bij de bot voor de jotihunt bot!", reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/start')]]))
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
              'level': 25}
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


def create_updater():
    updater = Updater(token=settings.Settings().bot_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    return updater