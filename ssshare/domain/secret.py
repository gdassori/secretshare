from ssshare.domain import DomainObject
from ssshare.domain.session import ShareSession


class Secret(DomainObject):
    def __init__(self, secret: str):
        self._session = None
        self._shares = None
        self._quorum = None
        self._secret = secret

    @property
    def secret(self):
        return self._secret

    @property
    def shares(self):
        return self._shares

    @property
    def quorum(self):
        return self._quorum

    @classmethod
    def new(cls, secret: str, session: ShareSession = None, shares: int = 5, quorum: int = 3):
        i = cls(secret)
        i._session = session
        i._shares = shares
        i._quorum = quorum
        return i

    def to_dict(self) -> dict:
        return dict(
            secret=self.secret,
            shares=self.shares,
            quorum=self.quorum
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'Secret':
        i = cls(data['secret'])
        i._quorum = data['quorum']
        i._shares = data['shares']
        return i