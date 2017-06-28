from enum import Enum

from ssshare.domain.master import SharedSessionMaster
from ssshare.domain.session import SharedSession
from ssshare.control import secret_share_repository


class SplitSessionType(Enum):
    # draft
    PRIVATE = 'private'
    AUDITABLE = 'auditable'


class SplitSession(SharedSession):
    def __init__(self, master: SharedSessionMaster=None, alias=None, repo=secret_share_repository):
        super().__init__(master=master, alias=alias, repo=repo)
        self._type = None

    @property
    def session_type(self):
        return self._type

    @classmethod
    def new(cls, master=None, alias=None, policies=None, repo=secret_share_repository):
        from ssshare.domain.secret import SharedSessionSecret
        i = cls(master=master, alias=alias, repo=repo)
        i._secret = SharedSessionSecret.new(session=i, shares=policies['shares'], quorum=policies['quorum'])
        return i

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid,
            master=self._master.to_dict(),
            last_update=self._last_update,
            alias=self._alias,
            users=[u.to_dict() for u in self.users],
            secret=self._secret and self._secret.to_dict()
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'SplitSession':
        from ssshare.domain.master import SharedSessionMaster
        from ssshare.domain.user import SharedSessionUser
        from ssshare.domain.secret import SharedSessionSecret
        i = cls(repo=repo)
        i._uuid = data['uuid']
        i._master = data.get('master') and SharedSessionMaster.from_dict(data['master'], session=i)
        i._last_update = data['last_update']
        i._alias = data['alias']
        i._users = [SharedSessionUser.from_dict(u, session=i) for u in data['users']]
        i._secret = data['secret'] and SharedSessionSecret.from_dict(data['secret'])
        i._secret._session = i._secret and i
        return i

    def to_api(self, auth=None):
        users = [self.master.to_api(auth=auth)] + [user.to_api(auth=auth) for user in self.users]
        return {
            'ttl': self.ttl,
            'users': users,
            'alias': self._alias,
            'secret': self._secret and self._secret.to_api(auth)
        }

    @property
    def secret(self):
        return self._secret and self._secret
