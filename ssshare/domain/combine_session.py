import time
import uuid
from enum import Enum
from ssshare import exceptions, settings
from ssshare.domain import DomainObject
from ssshare.domain.user import SharedSessionUser
from ssshare.control import secret_share_repository


class CombineSessionType(Enum):
    TRANSPARENT = 'transparent'  # All users obtain the redeemed secret
    FEDERATED = 'federated'  # The users must agree to release the secret only to the session master


class CombineSession(DomainObject):
    def __init__(self, master=None, alias=None, session_type=None, repo=secret_share_repository):
        self._type = session_type
        self._master = master
        self._repo = repo
        self._uuid = None
        self._users = {}
        self._secret = None
        self._alias = alias
        self._last_update = None
        self._session_ttl = settings.SESSION_TTL
        self._current_user = None
        self._shares = None

    @property
    def master(self):
        return self._master

    def get_user(self, user_id: str, alias: str = None):
        user = uuid.UUID(user_id) == self.master.uuid and self.master or self._users.get(user_id, None)
        return alias is not None and user and user.alias == alias and user or user

    @classmethod
    def new(cls, master=None, alias=None, session_type=None, repo=secret_share_repository):
        i = cls(master=master, alias=alias, repo=repo, session_type=session_type)
        return i

    @property
    def users(self):
        return list(self._users.values())

    @property
    def ttl(self):
        if not self._last_update:
            raise exceptions.SystemException('the object must be stored first')
        rem = self._session_ttl - (int(time.time()) - self._last_update)
        return self._session_ttl if self._session_ttl == -1 else rem > 0 and rem or 0

    @classmethod
    def get(cls, session_id: str, auth: str=None, repo=secret_share_repository) -> 'CombineSession':
        session = repo.get_session(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        i = cls.from_dict(session, repo=repo)
        return i

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid,
            last_update=self._last_update,
            alias=self._alias,
            users=[u.to_dict() for u in self.users],
            secret=self._secret and self._secret.to_dict()
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'CombineSession':
        from ssshare.domain.master import SharedSessionMaster
        from ssshare.domain.user import SharedSessionUser
        from ssshare.domain.secret import ShareSessionSecret
        i = cls(repo=repo)
        i._uuid = data['uuid']
        i._master = data.get('master') and SharedSessionMaster.from_dict(data['master'], session=i)
        i._last_update = data['last_update']
        i._alias = data['alias']
        i._users = {u['uuid']: SharedSessionUser.from_dict(u, session=i) for u in data['users']}
        i._secret = data['secret'] and ShareSessionSecret.from_dict(data['secret'])
        return i

    @property
    def uuid(self) -> (None, uuid.UUID):
        return self._uuid

    def store(self) -> 'CombineSession':
        assert not self._uuid
        self._last_update = int(time.time())
        res = self._repo.store_session(self.to_dict())
        self._uuid = res['uuid']
        return self

    def update(self) -> 'CombineSession':
        assert self._uuid
        self._last_update = int(time.time())
        self._repo.update_session(self.to_dict())
        return self

    def delete(self) -> bool:
        assert self._uuid
        self._repo.delete_session(self.to_dict())
        return True

    def to_api(self, auth=None):
        users = [user.to_api(auth=auth) for user in self.users]
        res = {
            'ttl': self.ttl,
            'users': users,
            'secret_sha256': self._secret and self._secret.sha256,
            'alias': self._alias,
        }
        if auth:
            res['secret'] = self._secret and self._secret.secret
        return res

    def _get_users_aliases(self) -> dict:
        return {
            user.alias: [user.ROLE, user_id] for user_id, user in self._users.items()
        }

    def join(self, alias: str):
        users = self._get_users_aliases()
        if alias in users:
            raise exceptions.ObjectDeniedException

        user = SharedSessionUser(user_id=uuid.uuid4(), alias=alias)
        self._users[str(user.uuid)] = user
        return user

    def add_share_from_payload(self, share: str) -> 'CombineSession':
        raise NotImplementedError