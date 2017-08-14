import traceback

import sys

from MyBotan import Botan
from PythonApi.RPApi.Base import Api as RPApi
import settings
import logging
import time
import PythonApi.jotihunt.Retrievers as jotihuntApi
import PythonApi.jotihunt.Base as jotihuntApiBase
import pickle
import os
from telegram.parsemode import ParseMode
import re
import imaplib
from PythonApi.scraperApi.Jotihuntscraper import get_hunts
from PythonApi.scraperApi.webscraper import to_dict
import threading

from reminders import Reminder

UPDATER_FILE = 'updater.jhu'

ALPHA, BRAVO, CHARLIE, DELTA, ECHO, FOXTROT, XRAY, PHOTOS, OPDRACHTEN, \
    NIEUWS, ERROR, HINTS = range(12)
my_updates_instance = None
__all__ = ['get_updates', 'ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO',
           'FOXTROT', 'XRAY', 'PHOTOS', 'OPDRACHTEN', 'NIEUWS', 'ERROR',
           'HINTS']

status_plaatjes = {
    'a': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADOAADxPsqAXmyBBClXTd4Ag'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADNAADxPsqAWy_jDGSfM8VAg'
        },
        'oranje': {''
                   'type': 'sticker',
                   'file_id': 'BQADBAADNgADxPsqAW5L5FGEVeZsAg'
                   }
    },
    'c': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADTAADxPsqAYLV3juZLpBdAg'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADSgADxPsqAT-u5My8rm3gAg'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADRgADxPsqAQV4dBO6m83XAg'
        }
    },
    'b': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADQAADxPsqAe0nAoB-ZMyOAg'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADQgADxPsqAYIFsuIiE6hzAg'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADRAADxPsqAWxDH1LIGSXKAg'
        }
    },
    'e': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADWgADxPsqAUL07wYDRvidAg'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADVAADxPsqAQsjZhRr4lEnAg'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADWAADxPsqATm-pA-vdphAAg'
        }
    },
    'd': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADTgADxPsqAZx6xRcZie8dAg'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADUgADxPsqAb2HyQa_q_n8Ag'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADUAADxPsqAQmw5iS__C7yAg'
        }
    },
    'f': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADXgADxPsqATT7K_u22oL7Ag'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADXAADxPsqAYLGQPHFp1xLAg'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADVgADxPsqAffXkv_Pldg-Ag'
        }
    },
    'x': {
        'groen': {
            'type': 'sticker',
            'file_id': 'BQADBAADOgADxPsqAU8tH66GcOAVAg'
        },
        'rood': {
            'type': 'sticker',
            'file_id': 'BQADBAADPAADxPsqASyb3aitvwQYAg'
        },
        'oranje': {
            'type': 'sticker',
            'file_id': 'BQADBAADPgADxPsqAbHyHKqDFGuLAg'
        }
    }

}
updater_lock = threading.Lock()


def get_updates():
    global updater_lock
    updater_lock.acquire()
    try:
        global my_updates_instance
        if my_updates_instance is None:
            try:
                if os.path.isfile(UPDATER_FILE):
                    with open(UPDATER_FILE, 'rb') as file:
                        my_updates_instance = MyUpdates()
                        d = pickle.load(file)
                        my_updates_instance.from_dict(d)
                        if my_updates_instance is None:
                            raise Exception('huh')
                else:
                    my_updates_instance = MyUpdates()
            except Exception as e:
                my_updates_instance = MyUpdates()
                my_updates_instance.error(e, 'startup error')
    finally:
        updater_lock.release()
    return my_updates_instance


def void_no_crash():
    def decorate(func):
        def call(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                type_, value_, traceback_ = sys.exc_info()
                logging.error(str(e), func.__name__)
                print(str(e))
                updates = get_updates()
                updates.error(e, func.__name__, (type_, value_, traceback_))

        return call

    return decorate


class MyUpdates:
    def __init__(self):
        self.t = None





        self._reminders_lock = threading.Lock()
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.seenHunts = dict()
        self.bot = None
        self.botan = Botan(settings.Settings().botan_key)
        self.rp_api = RPApi.get_instance(settings.Settings().rp_username,
                                         settings.Settings().rp_pass)
        self.messages = []  # list of tuples (int, str, str, tuple, dict)

        def get_kwargs_vos(new_item):
            if new_item['icon'] == '3':
                new_item['soort'] = 'Spot'
            elif new_item['icon'] == '4':
                new_item['soort'] = 'Hunt'
            else:
                new_item['soort'] = 'Hint'
            new_item['team_upper'] = new_item['team'].upper()
            new_item['tijd'] = new_item['datetime'][11:]
            return new_item.data

        def get_kwargs_vos_status(new_item):
            new_item['dg'] = new_item['team'][0].lower()
            return new_item._data

        def send_location(vos, chat_ids):
            bot = get_updates().bot
            if bot is not None:
                for chat_id in chat_ids:
                    bot.sendLocation(chat_id, latitude=vos['latitude'],
                                     longitude=vos['longitude'])

        def send_status_sticker(status, chat_ids):
            bot = get_updates().bot
            vos = status['dg']
            new_status = status['status']
            if bot is not None:
                for chat_id in chat_ids:
                    bot.sendSticker(chat_id,
                                    status_plaatjes[vos][new_status]['file_id']
                                    )
            send_cloudmessage(vos, new_status)

        message_vos = 'er is een {soort} ingevoerd voor {team}.\n' \
                      ' extra info: {extra}\n ' \
                      'opmerking/adres: {opmerking}\n' \
                      'tijd: {tijd}\n' \
                      'link: http://jotihunt2016.area348.nl/map.php?gebied=' \
                      '{team_upper}'
        message_vos_status = 'Er is een nieuwe status voor {team}'
        self.botan_id_vos = 'newLoc_{team}_{soort}'
        self.botan_id_vos_status = 'newStatus_{dg}_{status}'

        def get_retriever(dg):
            def retriever():
                return self.rp_api.vos(dg)
            return retriever

        def get_retriever_status(dg):
            def retriever():
                return jotihuntApi.get_vossen().data[dg]
            return retriever

        for dg in ['a', 'b', 'c', 'd', 'e', 'f', 'x']:
            retr1 = get_retriever(dg)
            updater_rp = SingleUpdater(retr1,
                                       get_kwargs_vos, message_vos,
                                       botan_id=self.botan_id_vos+'_'+dg,
                                       callback=send_location)
            retr = get_retriever_status(dg)
            updater_status = SingleUpdater(retr, get_kwargs_vos_status,
                                           message_vos_status,
                                           botan_id=self.botan_id_vos_status
                                           + '_'+dg,
                                           callback=send_status_sticker)
            if dg == 'a':
                self._A = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'b':
                self._B = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'c':
                self._C = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'd':
                self._D = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'e':
                self._E = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'f':
                self._F = SingleUpdateContainer([updater_rp, updater_status])
            elif dg == 'x':
                self._X = SingleUpdateContainer([updater_rp, updater_status])

        self._photos = set()  # naam niet veranderen
        get_last_opdracht = lambda: jotihuntApi.get_opdrachten().data[0]
        get_last_nieuws = lambda: jotihuntApi.get_nieuws_lijst().data[0]
        get_last_hint = lambda: jotihuntApi.get_hints().data[0]
        self.botan_id_jotihunt = 'new_{botan_soort}'

        def get_jotihunt_kwargs(new_response):
            r = dict()
            item = new_response.data
            r['title'] = item.titel
            if isinstance(item, jotihuntApiBase.Opdracht):
                r['url'] = settings.Settings().base_opdracht_url + item.ID
                r['soort'] = 'een nieuwe opdracht'
            elif isinstance(item, jotihuntApiBase.Hint):
                r['url'] = settings.Settings().base_hint_url + item.ID
                r['soort'] = 'een nieuwe hint'
            elif isinstance(item, jotihuntApiBase.Nieuws):
                r['url'] = settings.Settings().base_nieuws_url + item.ID
                r['soort'] = 'nieuws'
            r['botan_soort'] = r['soort'].replace(' ', '_')
            return r

        jotihunt_message = 'Er is {soort} met de titel [{title}]({url})'

        def add_opdracht_reminder(opdracht, chat_ids):
            opdracht_id = opdracht.data.ID
            if opdracht_id not in self.reminders:
                self._reminders_lock.acquire()
                try:
                    self.reminders[opdracht_id] = Reminder(opdracht, chat_ids)
                finally:
                    self._reminders_lock.release()
        opdracht_updater = SingleUpdater(get_last_opdracht,
                                         get_jotihunt_kwargs, jotihunt_message,
                                         botan_id=self.botan_id_jotihunt,
                                         callback=add_opdracht_reminder)
        nieuws_updater = SingleUpdater(get_last_nieuws, get_jotihunt_kwargs,
                                       jotihunt_message,
                                       botan_id=self.botan_id_jotihunt)
        hint_updater = SingleUpdater(get_last_hint, get_jotihunt_kwargs,
                                     jotihunt_message,
                                     botan_id=self.botan_id_jotihunt)
        self.reminders = dict()
        self._opdrachten = SingleUpdateContainer([opdracht_updater])  # naam niet
        # veranderen
        self._nieuws = SingleUpdateContainer([nieuws_updater])  # naam niet veranderen
        self._hints = SingleUpdateContainer([hint_updater])  # naam niet veranderen
        self._error = set()  # naam niet veranderen
        self._punten = {'opdrachten': 0,
                        'hints': 0,
                        'hunts': 0,
                        'fotos': 0,
                        'totaal': 0}

        self._last_update = 0
        self.lastPhoto = None
        self.seenMail = set()
        self.lastHint = None

    def to_dict(self):
        return {'A': self._A.chat_ids,
                'B': self._B.chat_ids,
                'C': self._C.chat_ids,
                'D': self._D.chat_ids,
                'E': self._E.chat_ids,
                'F': self._F.chat_ids,
                'X': self._X.chat_ids,
                'photos': self._photos,
                'opdrachten': self._opdrachten.chat_ids,
                'nieuws': self._nieuws.chat_ids,
                'error': self._error,
                'hints': self._hints.chat_ids,
                }

    @void_no_crash()
    def from_dict(self, d):
        for k in d:
            s =getattr(self, '_' + k)
            for chat_id in d[k]:
                s.add(chat_id)

    @void_no_crash()
    def update(self):
        if self._last_update is None or abs(time.time() -
                                                    self._last_update) > 60:
            threads = [threading.Thread(target=self._A.update),
                       threading.Thread(target=self._B.update),
                       threading.Thread(target=self._C.update),
                       threading.Thread(target=self._D.update),
                       threading.Thread(target=self._E.update),
                       threading.Thread(target=self._F.update),
                       threading.Thread(target=self._X.update),
                       threading.Thread(target=self._nieuws.update),
                       threading.Thread(target=self._opdrachten.update),
                       threading.Thread(target=self._hints.update),
                       threading.Thread(target=self.remind)]
            for t in threads:
                t.start()
            self.update_foto_opdracht()
            # self.update_mail()
            self.update_hunts()
            self._last_update = time.time()
            start = time.time()
            while threads:
                if time.time() - start > 300:
                    self.send_message(-158130982, 'timeout error opgetrden '
                                                  'tijdens updaten. updaten '
                                                  'duurde meer dan 300 '
                                                  'seconden. waarschijnlijk '
                                                  'is het een goed idee om '
                                                  'de bot opnieuw op te '
                                                  'starten.')
                    raise TimeoutError('meer dan 5 minuten over een update '
                                       'gedaan.', len(threads))
                t = threads.pop(0)
                t.join(1)
                if t.isAlive():
                    threads.append(t)

        else:
            return

    @void_no_crash()
    def remind(self):
        self._reminders_lock.acquire()
        try:
            for opdracht_id in self.reminders:
                self.reminders[opdracht_id].remind()
        finally:
            self._reminders_lock.release()

    @void_no_crash()
    def save(self):
        d = self.to_dict()
        with open(UPDATER_FILE, 'wb') as file:
            pickle.dump(d, file)

    @void_no_crash()
    def add_bot(self, bot):
        if self.bot is None:
            self.bot = bot
        for m in self.messages:
            chat_id, mesg, botan_id, args, kwargs = m
            mes = bot.send_message(chat_id, mesg, *args, **kwargs)
            if botan_id is not None:
                self.botan.track(mes, str(botan_id))
        self.messages = []

    def has_bot(self):
        return self.bot is not None

    def check_updates(self, chat_id):
        if chat_id in self._A:
            yield 'Alpha'
        if chat_id in self._B:
            yield 'Bravo'
        if chat_id in self._C:
            yield 'Charlie'
        if chat_id in self._D:
            yield 'Delta'
        if chat_id in self._E:
            yield 'Echo'
        if chat_id in self._F:
            yield 'Foxtrot'
        if chat_id in self._X:
            yield 'X-Ray'
        if chat_id in self._error:
            yield 'Errors'
        if chat_id in self._nieuws:
            yield 'Nieuws'
        if chat_id in self._opdrachten:
            yield 'Opdrachten'
        if chat_id in self._photos:
            yield 'photos'
        if chat_id in self._hints:
            yield 'hints'

    @void_no_crash()
    def add_chat(self, chat_id, update_type):
        if update_type == ALPHA:
            self._A.add(chat_id)
        elif update_type == BRAVO:
            self._B.add(chat_id)
        elif update_type == CHARLIE:
            self._C.add(chat_id)
        elif update_type == DELTA:
            self._D.add(chat_id)
        elif update_type == ECHO:
            self._E.add(chat_id)
        elif update_type == FOXTROT:
            self._F.add(chat_id)
        elif update_type == XRAY:
            self._X.add(chat_id)
        elif update_type == PHOTOS:
            self._photos.add(chat_id)
        elif update_type == OPDRACHTEN:
            self._opdrachten.add(chat_id)
        elif update_type == NIEUWS:
            self._nieuws.add(chat_id)
        elif update_type == ERROR:
            self._error.add(chat_id)
        elif update_type == HINTS:
            self._hints.add(chat_id)

    @void_no_crash()
    def remove_chat(self, chat_id, update_type):
        if update_type == ALPHA:
            self._A.remove(chat_id)
        elif update_type == BRAVO:
            self._B.remove(chat_id)
        elif update_type == CHARLIE:
            self._C.remove(chat_id)
        elif update_type == DELTA:
            self._D.remove(chat_id)
        elif update_type == ECHO:
            self._E.remove(chat_id)
        elif update_type == FOXTROT:
            self._F.remove(chat_id)
        elif update_type == XRAY:
            self._X.remove(chat_id)
        elif update_type == PHOTOS:
            self._photos.remove(chat_id)
        elif update_type == OPDRACHTEN:
            self._opdrachten.remove(chat_id)
        elif update_type == NIEUWS:
            self._nieuws.remove(chat_id)
        elif update_type == ERROR:
            self._error.remove(chat_id)
        elif update_type == HINTS:
            self._hints.remove(chat_id)

    @void_no_crash()
    def set_updates(self, chat_id, dg, status):
        if status:
            self.add_chat(chat_id, dg)
        else:
            self.remove_chat(chat_id, dg)

    @void_no_crash()
    def update_foto_opdracht(self, new_update_item=None):
        pass

    @void_no_crash()
    def update_mail(self, new_update_item=None):
        i = 1
        found = []
        gmail = imaplib.IMAP4_SSL('imap.gmail.com')
        gmail.login(settings.Settings().rpmail_username,
                        settings.Settings().rpmail_pass)
        gmail.select('INBOX')
        gmail.search(None, 'ALL')
        while True:
            j = bytes(str(i), 'utf8')
            try:
                status, mail = gmail.fetch(j, '(RFC822)')
            except Exception as e:
                type_, value_, traceback_ = sys.exc_info()
                get_updates().error(e, 'update_mail', (type_, value_, traceback_))
                break
            if mail[0] is None:
                break
            raw_text = mail[0][1].decode('utf8')
            result = re.search('de opdracht(.)*?deze opdracht', raw_text, re.S)
            if result is not None and result.group(0) not in self.seenMail:
                found.append(result.group(0))
                self.seenMail.add(result.group(0))
            result = re.search(
                'Jullie tegenhunt(.)*?mag uiteraard wel',
                raw_text, re.S)
            if result is not None and result.group(0) not in self.seenMail:
                found.append(result.group(0))
                self.seenMail.add(result.group(0))
            i += 1
        for update in found:
            for chat_id in self._nieuws:
                self.send_message(chat_id,
                                     'Er is een mail van de organisatie:\n'
                                     + str(update))

    @void_no_crash()
    def update_hunts(self, new_update_item=None):
        if settings.Settings().phpsessid is None:
            return
        h = get_hunts()
        hd = to_dict(*h)
        for k, v in enumerate(hd):
            if k not in self.seenHunts:
                if str(k).lower().startswith('a'):
                    for chat_id in self._A:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                elif str(k).lower().startswith('b'):
                    for chat_id in self._B:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                elif str(k).lower().startswith('c'):
                    for chat_id in self._C:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                elif str(k).lower().startswith('d'):
                    for chat_id in self._D:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                elif str(k).lower().startswith('e'):
                    for chat_id in self._E:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                elif str(k).lower().startswith('f'):
                    for chat_id in self._F:
                        self.send_message(chat_id, 'code: ' + str(
                            k) + ' is ingevoerd op de website')
                self.seenHunts[k] = v
            else:
                if v['status'] != self.seenHunts[k]['status']:
                    message = 'de status van code: {code} is aangepast op de website. Van {old_status} naar {new_status}. Het aantal punten voor deze hunt is nu: {punten}'
                    message = message.format(code=str(k),
                                             old_status=str(
                                                 self.seenHunts[k][
                                                     'status']),
                                             new_status=str(v['status']
                                                            ),
                                             puntten=str(v['punten']))
                    if str(k).lower().startswith('a'):
                        for chat_id in self._A:
                            self.send_message(chat_id, message)
                    elif str(k).lower().startswith('b'):
                        for chat_id in self._B:
                            self.send_message(chat_id, message)
                    elif str(k).lower().startswith('c'):
                        for chat_id in self._C:
                            self.send_message(chat_id, message)
                    elif str(k).lower().startswith('d'):
                        for chat_id in self._D:
                            self.send_message(chat_id, message)
                    elif str(k).lower().startswith('e'):
                        for chat_id in self._E:
                            self.send_message(chat_id, message)
                    elif str(k).lower().startswith('f'):
                        for chat_id in self._F:
                            self.send_message(chat_id, message)
                    else:
                        for chat_id in self._nieuws:
                            self.send_message(chat_id, message)
                    self.seenHunts[k] = v

    def error(self, e, func_name, tb=None):
        logging.info('updates error send to user:' + str(e) + ' ' + func_name)
        for chat_id in self._error:
            tb_s = ''
            if tb is not None:
                ex = traceback.format_exception(*tb)
                for l in ex:
                    tb_s += l
            message = "er is een error opgetreden:\n {funcname}\n{e}\n"\
                      "{clse}\n {tb}".format(funcname=str(func_name),
                                             e=str(e), clse=e.__class__,
                                             tb=tb_s)
            print(message)
            self.send_message(chat_id, message)

    @void_no_crash()
    def to_all(self, message):
        self.update()
        d = self.to_dict()
        chat_ids = set()
        for key in d:
            if type(d[key]) == set:
                for chat_id in d[key]:
                    chat_ids.add(chat_id)
        for chat_id in chat_ids:
            self.send_message(chat_id, message)

    def send_message(self, chat_id, message, *args, botan_id=None, **kwargs):
        message = message[:4096]
        if self.bot is None:
            self.messages.append((chat_id, message, botan_id, args, kwargs))
        else:
            m = self.bot.sendMessage(chat_id, message, *args, **kwargs)
            if botan_id is not None:
                self.botan.track(m, botan_id)

    def add_stopable_thread(self, t):
        if self.t is None:
            self.t = t

    def exit(self):
        if self.t is not None:
            self.t.stop()
        self.to_all('de bot gaat afsluiten.')
        self.error(Exception("de bot gaat stoppen"), "de bot gaat stoppen")



class SingleUpdater:
    def __init__(self, get_item_callback, get_message_kwargs, message,
                 only_last=True, callback=None, botan_id=None):
        """

        :param get_item_callback: takes no arguments and returns an
        comparable item.
        :param get_message_kwargs: takes the return value from
        get_item_callback and returns a dict. It will be called as
        message.format(**get_message_kwargs(new_item))
        :param message: the message to be send on an update. it will be
        formatted with the dict from get_message_kwargs
        :param only_last: True if something is an update if it is different
        from the last item. False if something is an update if it is different
        from all earlier items.
        :param callback: called upon an update as callback(new_item, chat_ids).
        can be None
        :param botan_id: an id for what kind of message the bot sends. it
        will be formatted with the dict from get_message_kwargs
        """
        self.seenStuff = set()
        self.lastSeen = None
        self.callback = callback
        self.get_item_callback = get_item_callback
        self.only_last = only_last
        self.message = message
        self.get_message_kwargs = get_message_kwargs
        self.chat_ids = set()
        self.botan_id = botan_id

    def feed_new_item(self, new_item):
        self.lastSeen = new_item
        if not self.only_last:
            self.seenStuff.add(new_item)
        message = self.message
        kwargs = self.get_message_kwargs(new_item)
        message = message.format(**kwargs)
        u = get_updates()
        botan_id = self.botan_id.format(**kwargs)
        for chat_id in self.chat_ids:
            u.send_message(chat_id, message, botan_id=botan_id,
                           parse_mode=ParseMode.MARKDOWN)
        if self.callback is not None:
            self.callback(new_item, self.chat_ids)

    @void_no_crash()
    def update(self):
        new_item = self.get_item_callback()
        if self.only_last:
            is_new = self.lastSeen != new_item
        else:
            is_new = new_item not in self.seenStuff
        if is_new:
            self.feed_new_item(new_item)

    def add(self, chat_id):
        return self.chat_ids.add(chat_id)

    def remove(self, chat_id):
        return self.chat_ids.remove(chat_id)

    def __contains__(self, item):
        return item in self.chat_ids

    def __iter__(self):
        for chat_id in self.chat_ids:
            yield chat_id


class SingleUpdateContainer:
    def __init__(self, updaters=None):
        if updaters is None:
            updaters = []
        self.updaters = set()
        self.chat_ids = set()
        for updater in updaters:
            self.add_updater(updater)

    def add_updater(self, updater):
        self.updaters.add(updater)
        for chat_id in updater:
            self.add(chat_id)

    def add(self, chat_id):
        self.chat_ids.add(chat_id)
        for updater in self.updaters:
            updater.add(chat_id)

    def remove(self, chat_id):
        self.chat_ids.remove(chat_id)
        for updater in self.updaters:
            updater.remove(chat_id)

    def update(self):
        for updater in self.updaters:
            updater.update()

    def __contains__(self, item):
        return item in self.chat_ids

    def __iter__(self):
        yield from self.chat_ids


def send_cloudmessage(vos, status):
    key = settings.Settings().firebase_key
    data = {'vos': vos, 'status': status}

