import random
import requests
from PythonApi.jotihunt.Base import Response, NIEUWS, OPDRACHT, NIEUWSLIJST,\
    HINTS, HINT, OPDRACHTEN, SCORELIJST, VOSSEN

try:
    from tokens import DEBUG
except:
    DEBUG = False


_base_url = "http://www.jotihunt.net/api/1.0/"
test_opdrachten = {
    'id0': {
        "ID": 'id0',
        "titel": "titel0",
        "datum": 1475268120,
        "inhoud": "html text id0",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id1': {
        "ID": 'id1',
        "titel": "titel1",
        "datum": 1475268120,
        "inhoud": "html text id1",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id2': {
        "ID": 'id2',
        "titel": "titel2",
        "datum": 1475268120,
        "inhoud": "html text id2",
        "eindtijd": 1476475200,
        "maxpunten": 2
    },
    'id3': {
        "ID": 'id3',
        "titel": "titel3",
        "datum": 1475268120,
        "inhoud": "html text id3",
        "eindtijd": 1476475200,
        "maxpunten": 4
    },
}
test_hint = {
    'id0': {
        "ID": 'id0',
        "titel": "titel0",
        "datum": 1475268120,
        "inhoud": "html text id0",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id1': {
        "ID": 'id1',
        "titel": "titel1",
        "datum": 1475268120,
        "inhoud": "html text id1",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id2': {
        "ID": 'id2',
        "titel": "titel2",
        "datum": 1475268120,
        "inhoud": "html text id2",
        "eindtijd": 1476475200,
        "maxpunten": 2
    },
    'id3': {
        "ID": 'id3',
        "titel": "titel3",
        "datum": 1475268120,
        "inhoud": "html text id3",
        "eindtijd": 1476475200,
        "maxpunten": 4
    },
}
test_nieuws = {
    'id0': {
        "ID": 'id0',
        "titel": "titel0",
        "datum": 1475268120,
        "inhoud": "html text id0",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id1': {
        "ID": 'id1',
        "titel": "titel1",
        "datum": 1475268120,
        "inhoud": "html text id1",
        "eindtijd": 1476475200,
        "maxpunten": 3
    },
    'id2': {
        "ID": 'id2',
        "titel": "titel2",
        "datum": 1475268120,
        "inhoud": "html text id2",
        "eindtijd": 1476475200,
        "maxpunten": 2
    },
    'id3': {
        "ID": 'id3',
        "titel": "titel3",
        "datum": 1475268120,
        "inhoud": "html text id3",
        "eindtijd": 1476475200,
        "maxpunten": 4
    },
}

def get_nieuws(nieuws_id):
    if not DEBUG:
        url = _base_url + "nieuws/" + str(nieuws_id)
        r = requests.get(url)
        json = r.json()
        return Response(json, NIEUWS)
    else:
        return Response({'version': "1.0",
                'last_update': 1475611690,
                'data': [test_nieuws[nieuws_id]]},NIEUWS)


def get_opdracht(opdracht_id):
    if not DEBUG:
        url = _base_url + "opdracht/" + str(opdracht_id)
        r = requests.get(url)
        return Response(r.json(), OPDRACHT)
    else:
        return Response({'version': "1.0",
                'last_update': 1475611690,
                'data': [test_opdrachten[opdracht_id]]}, OPDRACHT)


def get_hint(hint_id):
    if not DEBUG:
        url = _base_url + "hint/" + str(hint_id)
        r = requests.get(url)
        return Response(r.json(), HINT)
    else:
        return Response({'version': "1.0",
                'last_update': 1475611690,
                'data': [test_hint[hint_id]]}, HINT)


def get_nieuws_lijst():
    if not DEBUG:
        url = _base_url + "nieuws"
        r = requests.get(url)
        json = r.json()
        return Response(json, NIEUWSLIJST)
    else:
        r = {'version': "1.0",
                'last_update': 1475611690,
                'data': []}
        used_ids = set()
        for i in range(len(test_nieuws)):
            n_id = random.choice(list(test_nieuws.keys()))
            while n_id in used_ids:
                n_id = random.choice(list(test_nieuws.keys()))
            used_ids.add(n_id)
            n = {
                    'ID': test_nieuws[n_id]['ID'],
                    'titel': test_nieuws[n_id]['titel'],
                    'datum': test_nieuws[n_id]['datum'],
                }
            r['data'].append(n)
        return Response(r, NIEUWSLIJST)

def get_opdrachten():
    if not DEBUG:
        url = _base_url + "opdracht"
        r = requests.get(url)
        return Response(r.json(), OPDRACHTEN)
    else:
        r = {'version': "1.0",
                'last_update': 1475611690,
                'data': []}
        used_ids = set()
        for i in range(len(test_opdrachten)):
            n_id = random.choice(list(test_opdrachten.keys()))
            while n_id in used_ids:
                n_id = random.choice(list(test_opdrachten.keys()))
            used_ids.add(n_id)
            n = {
                    'ID': test_opdrachten[n_id]['ID'],
                    'titel': test_opdrachten[n_id]['titel'],
                    'datum': test_opdrachten[n_id]['datum'],
                    'maxpunten': test_opdrachten[n_id]['maxpunten'],
                    'eindtijd': test_opdrachten[n_id]['eindtijd'],
                }
            r['data'].append(n)
        return Response(r, OPDRACHTEN)


def get_hints():
    if not DEBUG:
        url = _base_url + "hint"
        r = requests.get(url)
        return Response(r.json(), HINTS)
    else:

        r = {'version': "1.0",
                'last_update': 1475611690,
                'data': []}
        used_ids = set()
        for i in range(len(test_hint)):
            n_id = random.choice(list(test_hint.keys()))
            while n_id in used_ids:
                n_id = random.choice(list(test_hint.keys()))
            used_ids.add(n_id)
            n = {
                    'ID': test_hint[n_id]['ID'],
                    'titel': test_hint[n_id]['titel'],
                    'datum': test_hint[n_id]['datum'],
                }
            r['data'].append(n)
        return Response(r, HINTS)


def get_scorelijst():
    url = _base_url + "scorelijst"
    r = requests.get(url)
    return Response(r.json(), SCORELIJST)


def get_vossen():
    if not DEBUG:
        url = _base_url + "vossen"
        r = requests.get(url)
        json = r.json()
        json['data'].append({'team': 'XRay',
                            'status': 'oranje'})
        return Response(json, VOSSEN)
    else:
        statussen = ['rood', 'oranje', 'groen']
        return Response({'version': '1.0', 'last_update': 1475659554,
                'data':[
                    {"team": "Alpha", "status": random.choice(statussen)},
                    {"team": "Bravo", "status": random.choice(statussen)},
                    {"team": "Charlie", "status": random.choice(statussen)},
                    {"team": "Delta", "status": random.choice(statussen)},
                    {"team": "Echo", "status": random.choice(statussen)},
                    {"team": "Foxtrot", "status": random.choice(statussen)},
                    {"team": "XRay", "status": random.choice(statussen)}
                ]}, VOSSEN)
