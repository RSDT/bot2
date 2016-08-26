# from telegram.contrib.botan import Botan
from MyBotan import Botan
from PythonApi.RPApi.Base import Api as RPApi
import tokens
import logging
import time
import PythonApi.jotihunt.Retrievers as jotihuntApi
import pickle
import os

UPDATER_FILE = 'updater.jhu'

ALPHA, BRAVO, CHARLIE, DELTA, ECHO, FOXTROT, XRAY, PHOTOS, OPDRACHTEN, NIEUWS, ERROR, HINTS = range(12)
my_updates_instance = None
__all__ = ['get_updates', 'ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'XRAY',
           'PHOTOS', 'OPDRACHTEN', 'NIEUWS', 'ERROR', 'HINTS']

status_plaatjes = {'a': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADOAADxPsqAXmyBBClXTd4Ag'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADNAADxPsqAWy_jDGSfM8VAg'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADNgADxPsqAW5L5FGEVeZsAg'}},
                   'c': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADTAADxPsqAYLV3juZLpBdAg'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADSgADxPsqAT-u5My8rm3gAg'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADRgADxPsqAQV4dBO6m83XAg'}},
                   'b': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADQAADxPsqAe0nAoB-ZMyOAg'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADQgADxPsqAYIFsuIiE6hzAg'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADRAADxPsqAWxDH1LIGSXKAg'}},
                   'e': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADWgADxPsqAUL07wYDRvidAg'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADVAADxPsqAQsjZhRr4lEnAg'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADWAADxPsqATm-pA-vdphAAg'}},
                   'd': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADTgADxPsqAZx6xRcZie8dAg'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADUgADxPsqAb2HyQa_q_n8Ag'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADUAADxPsqAQmw5iS__C7yAg'}},
                   'f': {'groen': {'type': 'sticker', 'file_id': 'BQADBAADXgADxPsqATT7K_u22oL7Ag'},
                         'rood': {'type': 'sticker', 'file_id': 'BQADBAADXAADxPsqAYLGQPHFp1xLAg'},
                         'oranje': {'type': 'sticker', 'file_id': 'BQADBAADVgADxPsqAffXkv_Pldg-Ag'}}}


def get_updates():
    global my_updates_instance
    if my_updates_instance is None:
        try:
            if os.path.isfile(UPDATER_FILE):
                with open(UPDATER_FILE, 'rb') as file:
                    my_updates_instance = pickle.load(file)
            else:
                my_updates_instance = MyUpdates()
        except:
            my_updates_instance = MyUpdates()
    return my_updates_instance


def void_no_crash():
    def decorate(func):
        def call(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.error(str(e), func.__name__)
                print(str(e))
                updates = get_updates()
                updates.error(e, func.__name__)

        return call

    return decorate


class MyUpdates:
    def __init__(self):
        self.bot = None
        self.botan = Botan(tokens.botan_key)
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
        self._error.add(-158130982)
        self._hints = set()
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
            self._last_update = time.time()
            pass
        else:
            return

    def save(self):
        with open(UPDATER_FILE, 'wb') as file:
            pickle.dump(self, file)

    @void_no_crash()
    def add_bot(self, bot):
        self.bot = bot

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
            yield  'Errors'
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
    def update_vos_last(self):
        vos_a = self.rp_api.vos('a')
        vos_b = self.rp_api.vos('b')
        vos_c = self.rp_api.vos('c')
        vos_d = self.rp_api.vos('d')
        vos_e = self.rp_api.vos('e')
        vos_f = self.rp_api.vos('f')
        vos_x = self.rp_api.vos('x')
        if self.lastA != vos_a and self.has_bot():
            self.lastA = vos_a
            for chat_id in self._A:
                self.new_vos(chat_id, 'Alpha', vos_a)
        if self.lastB != vos_b and self.has_bot():
            self.lastB = vos_b
            for chat_id in self._B:
                self.new_vos(chat_id, 'Bravo', vos_b)
        if self.lastC != vos_c and self.has_bot():
            self.lastC = vos_c
            for chat_id in self._C:
                self.new_vos(chat_id, 'Charlie', vos_c)
        if self.lastD != vos_d and self.has_bot():
            self.lastD = vos_d
            for chat_id in self._D:
                self.new_vos(chat_id, 'Delta', vos_d)
        if self.lastE != vos_e and self.has_bot():
            self.lastE = vos_e
            for chat_id in self._E:
                self.new_vos(chat_id, 'Echo', vos_e)
        if self.lastF != vos_f and self.has_bot():
            self.lastF = vos_f
            for chat_id in self._F:
                self.new_vos(chat_id, 'Foxtrot', vos_f)
        if self.lastX != vos_x and self.has_bot():
            self.lastX = vos_x
            for chat_id in self._X:
                self.new_vos(chat_id, 'X-Ray', vos_x)

    @void_no_crash()
    def new_vos(self, chat_id, deelgebied, vos):
        if vos['icon'] == '3':
            m = self.bot.sendMessage(chat_id, deelgebied + " Is gespot.\n " +
                                     "extra info: " + vos['extra'] + '\n' +
                                     'opmerking/adres: ' + vos['opmerking'])
        elif vos['icon'] == '4':
            m = self.bot.sendMessage(chat_id, deelgebied + " is geshunt.\n" +
                                     "extra info: " + vos['extra'] + '\n' +
                                     'opmerking/adres: ' + vos['opmerking'])
        else:
            m = self.bot.sendMessage(chat_id, "Er is een Hint ingevoerd voor " + str(deelgebied) + '\n' +
                                     'extra info: ' + str(vos['extra']) + '\n' +
                                     'opmerking/adres: ' + str(vos['opmerking']))
        self.bot.sendLocation(chat_id, latitude=vos['latitude'], longitude=vos['longitude'])
        self.botan.track(m, 'newLoc_'+deelgebied + '_' + vos['icon'])

    @void_no_crash()
    def update_vos_status(self):
        response = jotihuntApi.get_vossen()
        curr_status = response.data

        def send_update(chat_id, vos, new_status):
            if new_status is None:
                return
            m = self.bot.sendSticker(chat_id, status_plaatjes[vos][new_status])
            self.botan.track(m, 'vos_status_' + vos + '_' + new_status)
            send_cloudmessage(vos, new_status)

        def extract_status(vos):
            for item in curr_status:
                if item['team'][0].lower() == vos:
                    return item['status']

        def send_a():
            for chat_id in self._A:
                vos = 'a'
                send_update(chat_id, vos, extract_status(vos))

        def send_b():
            for chat_id in self._B:
                vos = 'b'
                send_update(chat_id, vos, extract_status(vos))

        def send_c():
            for chat_id in self._C:
                vos = 'c'
                send_update(chat_id, vos, extract_status(vos))

        def send_d():
            for chat_id in self._D:
                vos = 'd'
                send_update(chat_id, vos, extract_status(vos))

        def send_e():
            for chat_id in self._E:
                vos = 'e'
                send_update(chat_id, vos, extract_status(vos))

        def send_f():
            for chat_id in self._F:
                vos = 'f'
                send_update(chat_id, vos, extract_status(vos))

        def send_x():
            for chat_id in self._X:
                vos = 'x'
                send_update(chat_id, vos, extract_status(vos))
        if self.lastStatus is None:
            send_a()
            send_b()
            send_c()
            send_d()
            send_e()
            send_f()
            send_x()
            self.lastStatus = curr_status
        else:
            for item in curr_status:
                if item['team'] == 'Alpha' and item['status'] != extract_status('a')['status']:
                    send_a()
                if item['team'] == 'Bravo' and item['status'] != extract_status('b')['status']:
                    send_b()
                if item['team'] == 'Charlie' and item['status'] != extract_status('c')['status']:
                    send_c()
                if item['team'] == 'Delta' and item['status'] != extract_status('d')['status']:
                    send_d()
                if item['team'] == 'Echo' and item['status'] != extract_status('e')['status']:
                    send_e()
                if item['team'] == 'Foxtrot' and item['status'] != extract_status('f')['status']:
                    send_f()
                self.lastStatus = curr_status


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
        logging.info('updates error send to user:' + str(e) + ' ' + func_name)
        for chat_id in self._error:
            if self.has_bot():
                self.bot.sendMessage(chat_id, "er is een error opgetreden:\n" + str(func_name)+'\n'+str(e))


def send_cloudmessage(vos, status):
    key = tokens.firebase_key
    data = {'vos': vos, 'status': status}
