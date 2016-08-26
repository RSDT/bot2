from pythonApi.Base.Exceptions import NoSuchTypeException, RetrieveException

__all__ = ['SCORELIJST', 'OPDRACHT', 'OPDRACHTEN',
           'HINT', 'HINTS', 'NIEUWS',
           'NIEUWSLIJST', 'VOSSEN', 'Response']

OPDRACHT, OPDRACHTEN, HINT, HINTS, NIEUWS, NIEUWSLIJST, VOSSEN, SCORELIJST = range(8)


class Response:
    def __init__(self, json, kind):
        self.type = kind
        if 'error' in json:
            raise RetrieveException(json['error'])
        self.version = json['version']
        self.last_update = json['last_update']
        self.data = None
        if self.type == SCORELIJST:
            self.data = ScoreLijst(json["data"])
        elif self.type == OPDRACHT:
            self.data = Opdracht(json["data"][0])
        elif self.type == OPDRACHTEN:
            self.data = []
            from pythonApi.jotihunt.Retrievers import get_opdracht
            for opdracht in json["data"]:
                self.data.append(get_opdracht(opdracht["ID"]))
        elif self.type == HINT:
            self.data = Hint(json["data"][0])
        elif self.type == HINTS:
            self.data = []
            from pythonApi.jotihunt.Retrievers import get_hint
            for hint in json["data"]:
                self.data.append(get_hint(hint["ID"]))
        elif self.type == NIEUWS:
            self.data = Nieuws(json["data"][0])
        elif self.type == NIEUWSLIJST:
            self.data = []
            from pythonApi.jotihunt.Retrievers import get_nieuws
            for nieuws in json["data"]:
                self.data.append(get_nieuws(nieuws["ID"]))
        elif self.type == VOSSEN:
            self.data = Vos(json['data'])
        else:
            raise NoSuchTypeException(str(self.type))

    def __str__(self):
        data = ""
        if type(self.data) == list:
            data += '['
            for d in self.data:
                data += '\n' + str(d)
            data += '\n]'
        else:
            data = str(self.data)
        return '{\ntype: ' + str(self.type) + ',\nversion: ' + str(self.version) +\
               ',\nlast_update: ' + str(self.last_update) + ',\ndata:\n' + data + '\n}'


class Base:
    def __init__(self, json):
        self.ID = json['ID']
        self.titel = json['titel']
        self.inhoud = json['inhoud']
        self.datum = json['datum']

    def __str__(self):
        return str(self.titel)


class Opdracht(Base):
    def __init__(self, json):
        super(Opdracht, self).__init__(json)
        self.maxpunten = json['maxpunten']
        self.eindtijd = json['eindtijd']


class Hint(Base):
    def __init__(self, json):
        super(Hint, self).__init__(json)


class Nieuws(Base):
    def __init__(self, json):
        super(Nieuws, self).__init__(json)


class Vos:
    def __init__(self, json):
        self._data = dict()
        for vos in json:
            self._data[vos['team']] = vos['status']

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
