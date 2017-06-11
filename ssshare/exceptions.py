class WrongParametersException(Exception):
    pass


class SystemException(Exception):
    pass


class ObjectNotFoundException(Exception):
    pass


class ObjectExpiredException(Exception):
    pass


class ObjectDeniedException(Exception):
    pass


class DomainObjectBusyException(Exception):
    pass