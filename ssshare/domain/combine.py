import uuid
from enum import Enum
from ssshare.domain.session import SharedSession
from ssshare.control import secret_share_repository

class CombineSessionType(Enum):
    TRANSPARENT = 'transparent'  # All users obtain the redeemed secret
    FEDERATED = 'federated'  # The users must agree to release the secret only to the session master


class CombineSession(SharedSession):
    def __init__(self, master=None, alias=None, session_type=None, repo=secret_share_repository):
        super().__init__(master=master, alias=alias, repo=repo)
        self._type = session_type

    @classmethod
    def new(cls, session_id=None, master=None, alias=None, session_type=None, repo=secret_share_repository):
        _type = CombineSessionType(session_type)
        i = cls(master=master, alias=alias, repo=repo, session_type=_type)
        if session_id:
            i._uuid = uuid.UUID(session_id)
        return i

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid,
            last_update=self._last_update,
            alias=self._alias,
            users=[u.to_dict() for u in self.users],
            secret=self._secret and self._secret.to_dict(),
            type=self._type.value,
            master=self._master and self._master.to_dict()
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'CombineSession':
        from ssshare.domain.master import SharedSessionMaster
        from ssshare.domain.user import SharedSessionUser
        from ssshare.domain.secret import SharedSessionSecret
        i = cls(repo=repo)
        i._uuid = data['uuid']
        i._master = data.get('master') and SharedSessionMaster.from_dict(data['master'], session=i)
        i._last_update = data['last_update']
        i._alias = data['alias']
        i._users = {u['uuid']: SharedSessionUser.from_dict(u, session=i) for u in data['users']}
        i._secret = data['secret'] and SharedSessionSecret.from_dict(data['secret'])
        i._type = CombineSessionType(data['type'])
        return i

    def to_api(self, auth=None):
        users = [self.master.to_api(auth=auth)] + [user.to_api(auth=auth) for user in self.users]
        res = {
            'ttl': self.ttl,
            'users': users,
            'secret_sha256': self._secret and self._secret.sha256,
            'alias': self._alias,
            'type': self._type.value
        }
        if auth:
            res['secret'] = self._secret and self._secret.secret
        return res

    def add_share_from_payload(self, share: str) -> 'CombineSession':
        raise NotImplementedError