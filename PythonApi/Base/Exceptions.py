class JotiHuntException(Exception):
    pass


class NoSuchTypeException(JotiHuntException):
    pass


class RetrieveException(JotiHuntException):
    pass


class VerificationError(JotiHuntException):
    pass


class BannedError(JotiHuntException):
    pass


class NoDataError(JotiHuntException):
    pass


class UndocumatedStatusCodeError(JotiHuntException):
    pass


class IAmATheaPotError(JotiHuntException):
    pass
