import threading
from json import JSONDecodeError

import logging
import requests
from PythonApi.Base.Exceptions import VerificationError, BannedError, \
    NoDataError, UndocumatedStatusCodeError, IAmATheaPotError, UnkownKeyError
from hashlib import sha1
import json
import time

VOS, META, SC_ALL,\
FOTO_ALL, GEBRUIKER_INFO, TELEGRAM_LINK,\
CAR_ALL, CAR_NAMES, CAR_SINGLE,\
    CAR_INFO, CAR_DELETE = range(11)


def parse_time(tijd):
    # todo schrijf deze functie
    return tijd


def _retry_with_new_key_on_error(func):
    def decorate(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except VerificationError:
            self.api_key = None
            self.login()
            return func(self, *args, **kwargs)
    return decorate


class Api:
    instances = dict()
    instances_lock = threading.Lock()

    def __init__(self, username, hashed_password):
        self.lock = threading.Lock()
        self._api_key = None
        self.username = username
        self.hashed_password = hashed_password
        self.last_update = None
        self.api_key = None

        self.hunternaam = None
        self.api_key_lock = threading.Lock()
        self._base_url = 'http://jotihunt-API-V3.area348.nl/'

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, key):
        if self._api_key is None or key is not None:
            self._api_key = key

    @staticmethod
    def get_instance(username, password):
        with Api.instances_lock:
            if username not in Api.instances:
                hasher = sha1()
                hasher.update(password.encode('utf-8'))
                hashed_password = hasher.hexdigest()
                Api.instances[username] = Api(username, hashed_password)
            else:
                pass
            instances = Api.instances
            instance: Api = instances[username]
            return instance

    def _send_request(self, root, functie="", data=None):
        r_val = None
        try:
            if self.api_key is None and root != 'login':
                time.sleep(10)
                if self._api_key is None:
                    self.login()
            max_t = 24 * 60 * 60  # 1 dag
            if self.last_update is None or time.time() - self.last_update > max_t:
                raise UnkownKeyError(root)
            else:
                self.last_update = time.time()
            if data is None:
                url = self._base_url + root + '/' + self.api_key + '/' + functie
                r = requests.get(url, timeout=10)
            else:
                url = self._base_url + root + '/' + functie
                r = requests.post(url, data=json.dumps(data), timeout=10)
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
                    r_val = r.json()
                except JSONDecodeError as e:
                    r_val = None
            else:
                raise UndocumatedStatusCodeError((r.status_code, r.content))
        finally:
            pass
        return r_val

    _send_request_b = _send_request
    _send_request = _retry_with_new_key_on_error(_send_request_b)

    def hunter_namen(self):
        root = 'hunter'
        functie = 'hunter_namen/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return data

    def hunter_all(self, tijd=None):
        root = 'hunter'
        functie = 'all/'
        if tijd is not None:
            functie += parse_time(tijd) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return data

    def hunter_tail(self, hunter, tijd=None):
        root = 'hunter'
        functie = 'naam/tail/' + str(hunter) + '/'
        if tijd is not None:
            functie += parse_time(tijd) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return data

    @t_safe()
    def hunter_andere(self, hunter, tijd=None):
        root = 'hunter'
        functie = 'andere/' + str(hunter) + '/'
        if tijd is not None:
            functie += parse_time(tijd) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return data

    @t_safe()
    def hunter_single_location(self, hunter_id):
        root = 'hunter'
        functie = str(hunter_id) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return data

    @t_safe()
    def vos(self, team, tijd=None, vos_id=None):
        t = None
        if vos_id is None and tijd is None:
            result = self._vos_last(team)
        elif vos_id is not None and tijd is None:
            result = self._vos_single_location(team, vos_id)
        elif vos_id is None and tijd is not None:
            result = self._vos_all(team, tijd)
        else:
            result = None
        return Response(result, VOS)

    def _vos_last(self, team):
        root = 'vos'
        functie = team + '/last/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {"id":         "0",
    "datetime":    "2013-10-20 00:00:00",
    "latitude":     "0",
    "longitude":     "0",
    "team_naam":    team,
    "team":    team,
    "opmerking":     "lege data",
    "extra":    "lege data",
    "hint_nr":    "0",
    "icon":        "0"}
        return data

    def _vos_single_location(self, team, vos_id):
        root = 'vos'
        functie = team + '/' + str(vos_id) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return data

    def _vos_all(self, team, tijd):
        root = 'vos'
        functie = team + '/'
        if tijd is not None:
            functie += parse_time(tijd) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return data

    @t_safe()
    def meta(self):
        root = 'meta'
        functie = ''
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return Response(data, META)

    @t_safe()
    def sc_all(self):
        root = 'sc'
        functie = 'all/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return Response(data, SC_ALL)

    @t_safe()
    def foto_all(self):
        root = 'foto'
        functie = 'all/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return Response(data, FOTO_ALL)

    @t_safe()
    def gebruiker_info(self):
        root = 'gebruiker'
        functie = 'info/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = {}
        return Response(data, GEBRUIKER_INFO)

    @t_safe()
    def login(self):
        if self.last_update is not None and \
                                time.time() - self.last_update < \
                120:
            return
            # raise ToSoonReloginError(time.time() - self.last_update)
        self.api_key_lock.acquire()
        try:
            data = {'gebruiker': self.username, 'ww': self.hashed_password}
            root = 'login'
            self.last_update = time.time()
            response = self._send_request(root, data=data)
            sleutel = response['SLEUTEL']
            self.api_key = sleutel

        finally:
            self.api_key_lock.release()


    def send_telegram_user(self, telegramID, telegramVoornaam, telegramAchternaam='onbekend', telegramGebruikersnaam='onbekend'):
        data = {"SLEUTEL": self.api_key,
            "telegramID": telegramID,
            "telegramVoornaam":     telegramVoornaam or 'onbekend',
            "telegramAchternaam":    telegramAchternaam or 'onbekend',
            "telegramGebruikersnaam":     telegramGebruikersnaam or 'onbekend'}
        root = 'telegram'
        try:
            self._send_request(root, data=data)
        except JSONDecodeError as e:
            logging.error(e)
        except NoDataError as e:
            logging.error(e)
        except Exception as e:
            raise e


    def send_hunter_location(self, lat, lon, icon=0, hunternaam=None):
        if hunternaam is None:
            if self.hunternaam is None:
                hunternaam = self.username
            else:
                hunternaam = str(self.hunternaam)
        hunternaam = hunternaam + '-_:;=+telegram'
        data = {'SLEUTEL': self.api_key,
                'hunter': hunternaam,
                'latitude': str(lat),
                'longitude': str(lon),
                'icon': str(icon)}
        root = 'hunter'
        self._send_request(root, data=data)


    def send_vos_location(self, team, lat, lon, icon=0, info='-'):
        if self.hunternaam is None:
            hunternaam = self.username
        else:
            hunternaam = str(self.hunternaam)
        root = 'vos'
        data = {'SLEUTEL': self.api_key,
                'team': team,
                'hunter': hunternaam,
                'latitude': str(lat),
                'longitude': str(lon), 'icon': str(icon), 'info': str(info)}
        self._send_request(root, data=data)


    def get_telegram_link(self, telegram_id):
        root = 'telegram'
        functie = str(telegram_id) + '/'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = None
        return Response(data, TELEGRAM_LINK)


    def place_in_car(self, user_id, username, car_owner, role):
        root = 'auto'
        data = {'SLEUTEL': self.api_key,
                'gebruikersID': user_id,
                'gebruikersNaam': username,
                'autoEigenaar': car_owner,
                'rol': role}
        self._send_request(root, data=data)


    def get_car_names(self):
        root = 'auto'
        functie = 'distinct'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return Response(data, CAR_NAMES)


    def get_car_all(self):
        root = 'auto'
        functie = 'distinct/all'
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return Response(data, CAR_ALL)


    def get_car_by_name(self, name):
        root = 'car'
        functie = 'onecar/' + str(name)
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = []
        return Response(data, CAR_SINGLE)


    def get_car_info(self, id):
        root = 'car'
        functie = 'info/' + str(id)
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            data = None
        return Response(data, CAR_INFO)


    def remove_car_by_id(self, id):
        root = 'car'
        functie = 'removefromcarbyid/' + str(id)
        try:
            data = self._send_request(root, functie)
        except NoDataError as e:
            return False
        return Response(data['verwijderd'],CAR_DELETE)



class Response:
    def __init__(self, json, type):
        self.data = json
        self.type = type

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Response):
            return False
        elif other.type != self.type:
            return False
        elif self.type == VOS:
            return self.data['id'] == other.data['id']
        else:
            return self.data == other.data

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        yield from self.data
