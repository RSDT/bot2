import random

import requests

from PythonApi.jotihunt.Base import Response, NIEUWS, OPDRACHT, NIEUWSLIJST,\
    HINTS, HINT, OPDRACHTEN, SCORELIJST, VOSSEN

_base_url = "http://www.jotihunt.net/api/1.0/"


def get_nieuws(nieuws_id):
    url = _base_url + "nieuws/" + str(nieuws_id)
    r = requests.get(url)
    json = r.json()
    return Response(json, NIEUWS)


def get_opdracht(opdracht_id):
    url = _base_url + "opdracht/" + str(opdracht_id)
    r = requests.get(url)
    return Response(r.json(), OPDRACHT)


def get_hint(hint_id):
    url = _base_url + "hint/" + str(hint_id)
    r = requests.get(url)
    return Response(r.json(), HINT)


def get_nieuws_lijst():
    url = _base_url + "nieuws"
    r = requests.get(url)
    json = r.json()
    return Response(json, NIEUWSLIJST)


def get_opdrachten():
    url = _base_url + "opdracht"
    r = requests.get(url)
    return Response(r.json(), OPDRACHTEN)


def get_hints():
    url = _base_url + "hint"
    r = requests.get(url)
    return Response(r.json(), HINTS)


def get_scorelijst():
    url = _base_url + "scorelijst"
    r = requests.get(url)
    return Response(r.json(), SCORELIJST)


def get_vossen():
    debug = True
    url = _base_url + "vossen"
    r = requests.get(url)
    json = r.json()
    if debug:
        json['data'].append({'team': 'XRay',
                             'status': random.choice(['rood',
                                                      'oranje',
                                                      'groen'])})
    return Response(json, VOSSEN)
