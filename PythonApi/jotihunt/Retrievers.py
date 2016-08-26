import requests

from pythonApi.jotihunt.Base import Response, NIEUWS, OPDRACHT, NIEUWSLIJST, HINTS, HINT, OPDRACHTEN, SCORELIJST, VOSSEN

_base_url = "http://www.jotihunt.net/api/1.0/"


def get_nieuws(ID):
    url = _base_url + "nieuws/" + str(ID)
    r = requests.get(url)
    json = r.json()
    return Response(json, NIEUWS)


def get_opdracht(ID):
    url = _base_url + "opdracht/" + str(ID)
    r = requests.get(url)
    return Response(r.json(), OPDRACHT)


def get_hint(ID):
    url = _base_url + "hint/" + str(ID)
    r = requests.get(url)
    return Response(r.json(), HINT)


def get_nieuws_lijst():
    url = _base_url + "nieuws"
    r = requests.get(url)
    json = r.json()
    return Response(r.json(), NIEUWSLIJST)


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
    url = _base_url + "vossen"
    r = requests.get(url)
    return Response(r.json(), VOSSEN)
