from PythonApi.Base.Exceptions import NoSuchTypeException, RetrieveException
import time
import datetime

__all__ = ['SCORELIJST', 'OPDRACHT', 'OPDRACHTEN',
           'HINT', 'HINTS', 'NIEUWS',
           'NIEUWSLIJST', 'VOSSEN', 'Response']

OPDRACHT, OPDRACHTEN, HINT, HINTS, NIEUWS, NIEUWSLIJST, VOSSEN, SCORELIJST = \
    range(8)

def parse_time(timestamp) -> int:
    if isinstance(timestamp, int):
        return timestamp
    elif isinstance(timestamp, str):
        return time.mktime(datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S").timetuple())
    else:
        return timestamp

class Base:
    def __init__(self, json):
        self.ID = str(json['ID'])
        self.titel = str(json['titel'])
        self.inhoud = str(json['inhoud'])
        self.datum = parse_time(json['datum'])

    def __str__(self):
        return str(self.titel)


class Opdracht(Base):
    def __init__(self, json):
        super(Opdracht, self).__init__(json)
        self.maxpunten = json['maxpunten']
        self.eindtijd =  parse_time(json['eindtijd'])


class Hint(Base):
    def __init__(self, json):
        super(Hint, self).__init__(json)


class Nieuws(Base):
    def __init__(self, json):
        super(Nieuws, self).__init__(json)


class Vos:
    def __init__(self, team, status):
        self._data = dict()
        self._data['team'] = team
        self._data['status'] = status
        self.team = team
        self.status = status

    def __eq__(self, other):
        if other is None:
            return False
        return self.team == other.team and self.status == other.status

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError(str(item))


class ScoreLijst:
    def __init__(self, json):
        self.data = []
        for groep in json:
            self.data.append(ScoutingGroep(groep))


class ScoutingGroep:
    def __init__(self, json):
        self.plaats = json['plaats']
        self.groep = json['groep']
        self.woonplaats = json['woonplaats']
        self.regio = json['regio']
        self.hunts = json['hunts']
        self.opdrachten = json['opdrachten']
        self.fotoopdrachten = json['fotoopdrachten']
        self.hints = json['hints']
        self.totaal = json['totaal']


class Response:
    def __init__(self, json: dict, kind):
        self.type = kind
        if 'error' in json:
            raise RetrieveException(json['error'])
        self.version = json['version']
        self.last_update = parse_time(json.get('last_update', time.time()))
        self.data = None
        if self.type == SCORELIJST:
            self.data = ScoreLijst(json["data"])
        elif self.type == OPDRACHT:
            self.data = Opdracht(json["data"][0])
        elif self.type == OPDRACHTEN:
            self.data = []
            from PythonApi.jotihunt.Retrievers import get_opdracht
            for opdracht in json.get("data",  []):
                self.data.append(get_opdracht(opdracht["ID"]))
        elif self.type == HINT:
            self.data = Hint(json["data"][0])
        elif self.type == HINTS:
            self.data = []
            from PythonApi.jotihunt.Retrievers import get_hint
            for hint in json.get("data", []):
                self.data.append(get_hint(hint["ID"]))
        elif self.type == NIEUWS:
            self.data = Nieuws(json["data"][0])
        elif self.type == NIEUWSLIJST:
            self.data = []
            from PythonApi.jotihunt.Retrievers import get_nieuws
            for nieuws in json.get("data", []):
                self.data.append(get_nieuws(nieuws["ID"]))
        elif self.type == VOSSEN:
            self.data = dict()
            for v in json['data']:
                self.data[v['team'][0].lower()] = Vos(v['team'], v['status'])
        else:
            raise NoSuchTypeException(str(self.type))

    def __eq__(self, other):
        if other is None:
            return False
        if self.type != other.type:
            return False
        elif self.type in [OPDRACHT, HINT, NIEUWS]:
            return self.data.ID == other.data.ID
        elif self.type == VOSSEN:
            for k in self.data:
                if self.data[k].status != other.data[k].status:
                    return False
            return True
        else:
            return self.last_update == other.last_update

    def __str__(self):
        data = ""
        if type(self.data) == list:
            data += '['
            for d in self.data:
                data += '\n' + str(d)
            data += '\n]'
        else:
            data = str(self.data)
        return '{\ntype: ' + str(self.type) + ',\nversion: ' + str(
            self.version) + \
               ',\nlast_update: ' + str(self.last_update) + ',\ndata:\n' + \
               data + '\n}'
