from enum import Enum
from hashlib import sha256

from ssshare import exceptions, settings
from ssshare.domain import DomainObject
from ssshare.domain.split import SplitSession
from ssshare.domain.user import SharedSessionUser


class Share():
    def __init__(self, value: str, user=None):
        self.user = user
        self.value = value

    def to_dict(self):
        return {
            'user': self.user and str(self.user),
            'value': self.value
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(user=data['user'], value=data['value'])


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

    def user_have_share(self, user: SharedSessionUser):
        for share in self._splitted:
            if str(user.uuid) == share.user:
                return True

    @property
    def split_service(self):
        from ssshare.control import fxc_web_api_service
        return {
            SecretProtocol.FXC1: fxc_web_api_service
        }

    @property
    def combine_service(self):
        from ssshare.control import fxc_web_api_service
        return {
            SecretProtocol.FXC1: fxc_web_api_service
        }

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
        self._split()

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
            protocol=self._protocol and self._protocol.value,
            splitted=[s.to_dict() for s in self._splitted]
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'SharedSessionSecret':
        i = cls()
        i._secret = data['secret']
        i._quorum = data['quorum']
        i._shares = data['shares']
        i._protocol = SecretProtocol(data['protocol'])
        i._splitted = [Share(value=x['value'], user=x['user']) for x in data['splitted']]
        return i

    @property
    def sha256(self) -> str:
        return self._secret and sha256(self._secret.encode()).hexdigest()

    @property
    def splitted(self):
        if not self.secret:
            return []
        return self._splitted or self._split()

    @property
    def secret(self):
        return self._secret

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

    def _split(self):
        assert self._secret
        shares = self.split_service[self._protocol].split(self)
        for i, user in enumerate(self._session.users):
            shares[i].user = str(user.uuid)
        self._splitted = shares
        return self._splitted

    def attach_user_to_share(self, user: SharedSessionUser):
        for share in self._splitted:
            if not share.user:
                share.user = str(user.uuid)
                _s = share
                return _s
        raise exceptions.ObjectDeniedException

    def get_share(self, user: SharedSessionUser):
        assert self._splitted
        for share in self._splitted:
            if share.user == str(user.uuid):
                return share

    def add_share(self, share: Share):
        if len(self._splitted) < self.shares:
            self._splitted.append(share)
        if len(self._splitted) >= self.quorum:
            self.build_secret()
        raise exceptions.DomainObjectBusyException

    def build_secret(self):
        if len(self._splitted) >= self._shares:
            self._secret = self.combine_service[self._protocol].combine(self)
            return
        raise exceptions.ObjectNotFoundException
