from enum import Enum
from hashlib import sha256

from ssshare import exceptions, settings
from ssshare.domain import DomainObject
from ssshare.domain.split import SplitSession


class SecretProtocol(Enum):
    FXC1 = 'fxc1'


class SharedSessionSecret(DomainObject):
    def __init__(self):
        self._session = None
        self._shares = None
        self._quorum = None
        self._secret = None
        self._splitted = []

    def set_secret(self, value: dict):
        if self._secret:
            raise exceptions.ObjectDeniedException
        self._secret = value['value']
        self._protocol = SecretProtocol(value.get('protocol', 'fxc1'))
        return self

    @property
    def uuid(self):
        raise NotImplementedError

    @property
    def shares(self) -> int:
        return self._shares

    @property
    def quorum(self) -> int:
        return self._quorum

    @classmethod
    def new(cls,
            session: SplitSession = None,
            shares: int = 5,
            quorum: int = 3,
            protocol=settings.DEFAULT_SSS_PROTOCOL
            ):
        i = cls()
        i._session = session
        i._shares = shares
        i._quorum = quorum
        i._protocol = SecretProtocol(protocol)
        return i

    def to_dict(self) -> dict:
        return dict(
            secret=self.secret,
            shares=self.shares,
            quorum=self.quorum,
            protocol=self._protocol and self._protocol.value
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'SharedSessionSecret':
        i = cls()
        i._secret = data['secret']
        i._quorum = data['quorum']
        i._shares = data['shares']
        i._protocol = SecretProtocol(data['protocol'])
        return i

    @property
    def sha256(self) -> str:
        return self._secret and sha256(self._secret.encode()).hexdigest()

    @property
    def shares(self):
        return self._shares or []

    @property
    def secret(self):
        return self._secret

    def split(self):
        raise NotImplementedError

    def combine(self):
        assert not self.secret
        raise NotImplementedError

    def to_api(self, auth=None):
        res = {
            'quorum': self._quorum,
            'shares': self._shares,
            'sha256': self.sha256,
            'protocol': self._protocol.value
        }
        if self._session and auth and self._session.master and auth == str(self._session.master.uuid):
            res['secret'] = self._secret
        return res
