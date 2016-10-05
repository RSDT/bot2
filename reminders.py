import math
import requests

import Updates
import settings
import logging
import time
import random
from telegram import ParseMode
from tokens import DEBUG

url = 'https://mattijnkreuzen.nl/opdrachten/check_opdracht_klaar.php'


def convert_tijden(waarde, eenheid='seconden'):
    if eenheid in ['seconden', 's', 'seconds', 'second', 'seconde']:
        return waarde
    if eenheid in ['minuten', 'm', 'minutes', 'minuut', 'minute']:
        return convert_tijden(waarde * 60, 'seconden')
    if eenheid in ['uur', 'u', 'hour', 'uren', 'hours', 'h']:
        return convert_tijden(waarde * 60, 'minuten')
    if eenheid in ['dagen', 'd', 'days', 'dag', 'day']:
        return convert_tijden(waarde * 24, 'uur')


class Reminder:
    def __init__(self, opdracht, chat_ids):
        self.maxpunten = opdracht.data.maxpunten
        self.eindtijd = opdracht.data.eindtijd
        self.titel = opdracht.data.titel
        self.opdracht_id = opdracht.data.ID
        if not DEBUG:
            self.reminders = [[None, (1, 'dag'), (1, 'dag')],
                              [(1, 'dag'), (1, 'uur'), (2, 'uur')],
                              [(1, 'uur'), (30, 'minuten'), (10, 'minuten')],
                              [(30, 'minuten'), (10, 'minuten'), (5, 'minuten')],
                              [(15, 'minuten'), (3, 'minuten'), (3, 'minuten')],
                              [(3, 'minuten'), (0, 'minuten'), (1, 'minuten')],
                              [(0, 'minuten'), (-2, 'minuten'), (1, 'minuten')],
                              [(-2, 'minuten'), None, None]
                              ]
        else:
            self.reminders = [[None, (0, 'minuten'), (1, 'minuten')]]
        self.last_warning = 0
        self.chat_ids = chat_ids

    def check_remind(self):
        try:
            data = {
                'opdracht_id': self.opdracht_id,
                'naam': self.titel,
                'maxpunten': self.maxpunten,
                'eindtijd': self.eindtijd,
                'SLEUTEL': settings.Settings().SLEUTEL
            }
            r = requests.post(url=url, json=data)
            json = r.json()
            return json['verified']
        except Exception as e:
            logging.error('Login error, return True' + str(e))
            return True

    def remaining_time(self, eenheid='seconden'):
        """Return de tijd tot de opdracht moet worden ingeleverd in eenheid. """
        if eenheid is None or eenheid in ['seconden', 's', 'seconds',
                                          'second', 'seconde']:
            return self.eindtijd - time.time()
        if eenheid in ['minuten', 'm', 'minutes', 'minuut', 'minute']:
            return self.remaining_time() / 60
        if eenheid in ['uur', 'u', 'hour', 'uren', 'hours', 'h']:
            return self.remaining_time(eenheid='minuten') / 60
        if eenheid in ['dagen', 'd', 'days', 'dag', 'day']:
            return self.remaining_time(eenheid='uur') / 24
        else:
            return None

    def check_in_time(self):
        for reminder in self.reminders:
            if None in reminder:
                if reminder[0] is None:
                    reminder[0] = (self.remaining_time() + 9001, 'seconds')
                    while not reminder[0][0] > self.remaining_time(reminder[0][1]):
                        reminder[0] = (
                            self.remaining_time() + (
                            random.choice([1, -1]) * random.choice(
                                range(1000))),
                            'seconds')
                if reminder[1] is None:
                    reminder[1] = (self.remaining_time() - 9001, 'seconds')
                    while not reminder[1][0] > self.remaining_time(
                            reminder[1][1]):
                        reminder[1] = (
                            self.remaining_time() + (
                            random.choice([1, -1]) * random.choice(
                                range(1000))),
                            'seconds')
            if reminder[0][0] > self.remaining_time(reminder[0][1]) and \
                            reminder[1][
                                0] < self.remaining_time(reminder[1][1]):
                d_time = time.time() - self.last_warning
                if reminder[2] is not None and d_time > convert_tijden(
                        reminder[2][0], reminder[2][1]):
                    return True
        return False

    def send_reminder(self):
        self.last_warning = time.time()
        message = 'Reminder voor de opdracht: [{titel}]({url})\n' \
                  'Hier kunnen we {maxpunten} punt{mv} "mee ' \
                  'verdienen." We kunnen hier nog {uren} uur en ' \
                  '{min} minuten over doen.'
        message = message.format(titel=self.titel,
                                 url=settings.Settings(
                                 ).base_opdracht_url+self.opdracht_id,
                                 maxpunten=self.maxpunten,
                                 mv=('en' if self.maxpunten != 1
                                     else ''),
                                 uren=math.floor(
                                     self.remaining_time('uur')),
                                 min=math.floor(
                                     self.remaining_time(
                                         'minuten') % 60))
        u = Updates.get_updates()
        for chat_id in self.chat_ids:
            u.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)

    def remind(self):
        if self.check_in_time() and self.check_remind():
            self.send_reminder()
