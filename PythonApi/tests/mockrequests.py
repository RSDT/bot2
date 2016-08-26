status_code = 200

class FakeJsonParseError(Exception):
    pass


class Response:
    def __init__(self, url, data=None):
        self.status_code = status_code
        self.url = url
        self.content = "some content"
        self.data = data

    def json(self):
        if self.status_code != 200:  # er wordt geen json teruggegeven.
            raise FakeJsonParseError()
        if '/login' in self.url:
            return {'SLEUTEL': '1234A'}


def get(url):
    return Response(url)


def post(url, data):
    return Response(url, data=data)
