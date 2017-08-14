from telegram import TelegramError

trustedUsers = set()
trustedChats = set()
adminUsers = {"19594180"}

ie201
def check_authenticated(tg_user_id: mytypes.TgUserId, chat_id:mytypes.TgChatId) -> bool:
    global trustedUsers, trustedChats
    if tg_user_id in trustedUsers:
        return True
    if chat_id in trustedChats:
        trustedUsers.add(tg_user_id)
        return True

messages = set()
def authenticate_chat(updater:Updater, tg_user_id: mytypes.TgUserId, chat_id: mytypes.TgChatId, username="unkown",
                      chat_naam="unkown"):
    return True
    try:
        data = {
            'tg_user_id': tg_user_id,
            'chat_id': chat_id,
            'SLEUTEL': sleutel,
            'username': username,
            'chat_naam': chat_naam
        }
        r = requests.post(url=url, json=data)
        json = r.json()
        return json['verified']
    except Exception as e:
        logging.error('Login error, return True' + str(e)
        return True
    else:
        global messages
        x = random.randint(0, 100000)
        for admin in adminUsers:
            message = str(username) + " wil graag de bot gebruiken in de chat " + str(chat_naam) + "\n"  \
                      "Maar deze user en chat zijn nog niet geverifieërd. \n" \
                      "Wil je toestaan dat deze gekruiker de bot kan gebruiken? \n" \
                      "Je ontvangt dit bericht omdat je admin bent van de bot." + ":" + str(x)

            allowButton = telegram.InlineKeyboardButton("toestaan", callback_data="allow:"+str(tg_user_id) + ":"+ str(chat_id) +  ":" + str(x))
            denyButton = telegram.InlineKeyboardButton("niet toestaan", callback_data="deny:" + (str(tg_user_id) + ":"+ str(chat_id) + ":" + str(x)))

            allowchatButton = telegram.InlineKeyboardButton("alle gebruikers in de chat toestaan", callback_data="allow_chat:" + str(tg_user_id) + ":"+str(chat_id)
                                                            + ":" + str(x))
            keyboard = telegram.InlineKeyboardMarkup([[allowButton, denyButton, allowchatButton]])
            m: telegram.Message = updater.bot.send_message(admin, message, reply_markup=keyboard)
            messages.add(m)
        handler = telegram.ext.CallbackQueryHandler(onAdminCalback(str(x)))
        updater.dispatcher.add_handler(handler)
    return False


def onAdminCalback(x: str): #Callable[[telegram.Bot, telegram.Update],None]:
    global messages

    def callback(bot:telegram.Bot, update:telegram.Update):
        query: telegram.CallbackQuery = update.callback_query
        data: str = query.data
        if data.endswith(x):
            if data.startswith("allow"):
                user: telegram.User = update.effective_user
                extra_message = "is toegestaan door " + user.name
            elif data.startswith("deny"):
                user: telegram.User = update.effective_user
                extra_message = "is niet toegestaan door " + user.name
            elif data.startswith("allow"):
                user: telegram.User = update.effective_user
                extra_message = "Chat is toegevoegd door " + user.name
            else:
                user: telegram.User = update.effective_user
                extra_message="user niet toegevoegd error veroorzaakt door" + user.name
            done = set()
            for message in messages:
                if message.text.endswith(x):
                    try:
                        message.edit_text(message.text + "\n " + extra_message)
                        message.edit_reply_markup()
                        done.add(message)
                    except TelegramError:
                        pass
            for d in done:
                messages.remove(d)
    return callback
