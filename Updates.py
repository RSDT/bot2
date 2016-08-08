from telegram.contrib.botan import Botan
from pythonApi.RPApi.Base import Api as RPApi
import tokens
import logging
import time

ALPHA, BRAVO, CHARLIE, DELTA, ECHO, FOXTROT, XRAY, PHOTOS, OPDRACHTEN, NIEUWS, ERROR, HINTS = range(12)
my_updates_instance = None
__all__ = ['get_updates', 'ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'XRAY',
           'PHOTOS', 'OPDRACHTEN', 'NIEUWS', 'ERROR', 'HINTS']


def get_updates():
    global my_updates_instance
    if my_updates_instance is None:
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
        self._A.add(19594180)  # TODO remove this
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
                if vos_a['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Alpha.")
                    self.botan.track(m, 'newLocA0')
                    self.bot.sendLocation(chat_id, latitude=vos_a['latitude'], longitude=vos_a['longitude'])
                elif vos_a['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Alpha gespot.")
                    self.botan.track(m, 'newLocA1')
                    self.bot.sendLocation(chat_id, latitude=vos_a['latitude'], longitude=vos_a['longitude'])
                elif vos_a['icon'] == '2':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Alpha gehunt.")
                    self.botan.track(m, 'newLocA2')
                    self.bot.sendLocation(chat_id, latitude=vos_a['latitude'], longitude=vos_a['longitude'])
        if self.lastB != vos_b and self.has_bot():
            self.lastB = vos_b
            for chat_id in self._B:
                if vos_b['icon'] == '0':
                    m =self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Bravo.")
                    self.botan.track(m, 'newLocB0')
                    self.bot.sendLocation(chat_id, latitude=vos_b['latitude'], longitude=vos_b['longitude'])
                elif vos_b['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Bravo gespot.")
                    self.botan.track(m, 'newLocB1')
                    self.bot.sendLocation(chat_id, latitude=vos_b['latitude'], longitude=vos_b['longitude'])
                elif vos_b['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Bravo gehunt.")
                    self.botan.track(m, 'newLocB2')
                    self.bot.sendLocation(chat_id, latitude=vos_b['latitude'], longitude=vos_b['longitude'])
        if self.lastC != vos_c and self.has_bot():
            self.lastC = vos_c
            for chat_id in self._C:
                if vos_c['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Charlie.")
                    self.botan.track(m, 'newLocC0')
                    self.bot.sendLocation(chat_id, latitude=vos_c['latitude'], longitude=vos_c['longitude'])
                elif vos_c['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Charlie gespot.")
                    self.botan.track(m, 'newLocC1')
                    self.bot.sendLocation(chat_id, latitude=vos_c['latitude'], longitude=vos_c['longitude'])
                elif vos_c['icon'] == '2':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Charlie gehunt.")
                    self.botan.track(m, 'newLocC2')
                    self.bot.sendLocation(chat_id, latitude=vos_c['latitude'], longitude=vos_c['longitude'])
        if self.lastD != vos_d and self.has_bot():
            self.lastD = vos_d
            for chat_id in self._D:
                if vos_d['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Delta.")
                    self.botan.track(m, 'newLocD0')
                    self.bot.sendLocation(chat_id, latitude=vos_d['latitude'], longitude=vos_d['longitude'])
                elif vos_d['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Delta gespot.")
                    self.botan.track(m, 'newLocD1')
                    self.bot.sendLocation(chat_id, latitude=vos_d['latitude'], longitude=vos_d['longitude'])
                elif vos_d['icon'] == '2':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Delta gehunt.")
                    self.botan.track(m, 'newLocD2')
                    self.bot.sendLocation(chat_id, latitude=vos_d['latitude'], longitude=vos_d['longitude'])
        if self.lastE != vos_e and self.has_bot():
            self.lastE = vos_e
            for chat_id in self._E:
                if vos_e['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Echo.")
                    self.botan.track(m, 'newLocE0')
                    self.bot.sendLocation(chat_id, latitude=vos_e['latitude'], longitude=vos_e['longitude'])
                elif vos_e['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Echo gespot.")
                    self.botan.track(m, 'newLocE1')
                    self.bot.sendLocation(chat_id, latitude=vos_e['latitude'], longitude=vos_e['longitude'])
                elif vos_e['icon'] == '2':
                    self.bot.sendMessage(chat_id, " Heeft Vos Echo gehunt.")
                    self.botan.track(m, 'newLocE2')
                    self.bot.sendLocation(chat_id, latitude=vos_e['latitude'], longitude=vos_e['longitude'])
        if self.lastF != vos_f and self.has_bot():
            self.lastF = vos_f
            for chat_id in self._F:
                if vos_f['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor Foxtrot.")
                    self.botan.track(m, 'newLocF0')
                    self.bot.sendLocation(chat_id, latitude=vos_f['latitude'], longitude=vos_f['longitude'])
                elif vos_f['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Foxtrot gespot.")
                    self.botan.track(m, 'newLocF1')
                    self.bot.sendLocation(chat_id, latitude=vos_f['latitude'], longitude=vos_f['longitude'])
                elif vos_f['icon'] == '2':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos Foxtrot gehunt.")
                    self.botan.track(m, 'newLocF2')
                    self.bot.sendLocation(chat_id, latitude=vos_f['latitude'], longitude=vos_f['longitude'])
        if self.lastX != vos_x and self.has_bot():
            self.lastX = vos_x
            for chat_id in self._X:
                if vos_x['icon'] == '0':
                    m = self.bot.sendMessage(chat_id, " Heeft een hint locatie verstuurd voor X-Ray.")
                    self.botan.track(m, 'newLocX0')
                    self.bot.sendLocation(chat_id, latitude=vos_x['latitude'], longitude=vos_x['longitude'])
                elif vos_x['icon'] == '1':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos X-Ray gespot.")
                    self.botan.track(m, 'newLocX1')
                    self.bot.sendLocation(chat_id, latitude=vos_x['latitude'], longitude=vos_x['longitude'])
                elif vos_x['icon'] == '2':
                    m = self.bot.sendMessage(chat_id, " Heeft Vos X-Ray gehunt.")
                    self.botan.track(m, 'newLocX2')
                    self.bot.sendLocation(chat_id, latitude=vos_x['latitude'], longitude=vos_x['longitude'])

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
