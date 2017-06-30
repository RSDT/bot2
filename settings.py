import tokens


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        return self.instance()

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class Settings:
    def __init__(self):
        self.phpsessid = None
        self.bot_key = tokens.bot_key
        self.SLEUTEL = tokens.SLEUTEL
        self.rp_username = tokens.rp_username
        self.rp_pass = tokens.rp_pass
        self.botan_key = tokens.bot_key
        self.firebase_key = tokens.firebase_key
        self.base_opdracht_url = tokens.base_opdracht_url
        self.base_hint_url = tokens.base_hint_url
        self.base_nieuws_url = tokens.base_nieuws_url
        self.rpmail_username = tokens.rpmail_username
        self.rpmail_pass = tokens.rpmail_pass
