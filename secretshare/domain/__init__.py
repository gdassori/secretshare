import abc


class DomainObject(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self):
        pass  # pragma: no cover

    @abc.abstractproperty
    def uuid(self):
        pass