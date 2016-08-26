import requests
from pythonAPI.Base.Exceptions import VerificationError, BannedError, NoDataError, UndocumatedStatusCodeError, IAmATheaPotError
from hashlib import sha1
import json
import time


def parse_time(time):
    return time


class Api:
    instances = dict()

    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password
        self.last_update = None
        self.api_key = None
        self.hunternaam = None
        self._base_url = 'http://jotihunt-API_V2.area348.nl/'
        self.login()

    @staticmethod
    def get_instance(username, password):
        if username not in Api.instances:
            hasher = sha1()
            hasher.update(password.encode('utf-8'))
            hashed_password = hasher.hexdigest()
            Api.instances[username] = Api(username, hashed_password)
        else:
            pass
        return Api.instances[username]

    def _send_request(self, root, functie="", data=None):
        if self.last_update is None or time.time() - self.last_update > 24 * 60 * 60:
            self.login()
        else:
            self.last_update = time.time()
        if data is None:
            url = self._base_url + root + '/' + self.api_key + '/' + functie
            r = requests.get(url)
        else:
            url = self._base_url + root + '/' + functie
            r = requests.post(url, data=json.dumps(data))
        if r.status_code == 401:
            raise VerificationError(r.content)
        elif r.status_code == 403:
            raise BannedError(r.content)
        elif r.status_code == 404:
            raise NoDataError(r.content)
        elif r.status_code == 418:
            raise IAmATheaPotError(r.content)
        elif r.status_code == 200:
            try:
                return r.json()
            except:
                return
        else:
            raise UndocumatedStatusCodeError((r.status_code, r.content))

    def hunter_namen(self):
        root = 'hunter'
        functie = 'hunter_namen/'
        data = self._send_request(root, functie)
        return data

    def hunter_all(self, time=None):
        root = 'hunter'
        functie = 'all/'
        if time is not None:
            functie += parse_time(time) + '/'
        data = self._send_request(root, functie)
        return data

    def hunter_tail(self, hunter, time=None):
        root = 'hunter'
        functie = 'naam/tail/' + str(hunter) + '/'
        if time is not None:
            functie += parse_time(time) + '/'
        data = self._send_request(root, functie)
        return data

    def hunter_andere(self, hunter, time=None):
        root = 'hunter'
        functie = 'andere/' + str(hunter) + '/'
        if time is not None:
            functie += parse_time(time) + '/'
        data = self._send_request(root, functie)
        return data

    def hunter_single_location(self, id):
        root = 'hunter'
        functie = str(id) + '/'
        data = self._send_request(root, functie)
        return data

    def vos(self, team, time=None, id=None):
        if id is None and time is None:
            result = self._vos_last(team)
        elif id is not None and time is None:
            result = self._vos_single_location(team, id)
        elif id is None and time is not None:
            result = self._vos_all(team, time)
        else:
            result = None
        return result

    def _vos_last(self, team):
        root = 'vos'
        functie = team + '/last/'
        data = self._send_request(root, functie)
        return data

    def _vos_single_location(self, team, id):
        root = 'vos'
        functie = team + '/' + str(id) + '/'
        data = self._send_request(root, functie)
        return data

    def _vos_all(self, team, time):
        root = 'vos'
        functie = team + '/'
        if time is not None:
            functie += parse_time(time) + '/'
        data = self._send_request(root, functie)
        return data

    def meta(self):
        root = 'meta'
        functie = ''
        data = self._send_request(root, functie)
        return data

    def sc_all(self):
        root = 'sc'
        functie = 'all/'
        data = self._send_request(root, functie)
        return data

    def foto_all(self):
        root = 'foto'
        functie = 'all/'
        data = self._send_request(root, functie)
        return data

    def gebruiker_info(self):
        root = 'gebruiker'
        functie = 'info/'
        data = self._send_request(root, functie)
        return data

    def login(self):
        data = {'gebruiker': self.username, 'ww': self.hashed_password}
        root = 'login'
        self.last_update = time.time()
        sleutel = self._send_request(root, data=data)['SLEUTEL']
        self.api_key = sleutel

    def send_hunter_location(self, lat, lon, icon=0):
        if self.hunternaam is None:
            hunternaam = self.username
        else:
            hunternaam = str(self.hunternaam)
        data = {'SLEUTEL': self.api_key, 'hunter':hunternaam, 'latitude': str(lat), 'longitude': str(lon), 'icon': str(icon)}
        root = 'hunter'
        self._send_request(root, data=data)

    def send_vos_location(self, team, lat, lon, icon=0, info='-'):
        if self.hunternaam is None:
            hunternaam = self.username
        else:
            hunternaam = str(self.hunternaam)
        root = 'vos'
        data = {'SLEUTEL': self.api_key, 'team': team, 'hunter': hunternaam, 'latitude': str(lat),
                'longitude': str(lon), 'icon': str(icon), 'info': str(info)}
        self._send_request(root, data=data)