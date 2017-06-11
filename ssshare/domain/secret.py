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
        self._protocol = SecretProtocol(settings.DEFAULT_SSS_PROTOCOL)

    def edit_secret(self, value: dict):
        value.get('value') and self._set_secret(value['value'])
        value.get('shares') and self._set_shares(value['shares'])
        value.get('quorum') and self._set_quorum(value['quorum'])
        value.get('protocol') and SecretProtocol(value.get('protocol', 'fxc1'))
        return self

    def _set_secret(self, secret: str):
        if self._secret:
            raise exceptions.ObjectDeniedException
        self._secret = secret

    def _set_shares(self, shares: int):
        if shares < len(self._session.users):
            raise exceptions.WrongParametersException('shares < users')
        self._shares = shares

    def _set_quorum(self, quorum: int):
        if quorum >= self._shares:
            raise exceptions.WrongParametersException('quorum >= shares')
        self._quorum = quorum

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
            protocol=None
            ):
        i = cls()
        i._session = session
        i._shares = shares
        i._quorum = quorum
        if protocol:
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
