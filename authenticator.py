import requests
import logging

#url = 'https://mattijnkreuzen.nl/tg_users/telegramusers.php'

def authenticate_chat(tg_user_id, chat_id, sleutel, username="unkown",
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
        logging.error('Login error, return True' + str(e))
        return True
