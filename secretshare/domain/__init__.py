import abc


class DomainObject(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def uuid(self):
        pass