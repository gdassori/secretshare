import abc
import time
import uuid
from ssshare import exceptions, settings
from ssshare.control import secret_share_repository
from ssshare.domain import DomainObject
from ssshare.domain.user import SharedSessionUser


class SharedSession(DomainObject, metaclass=abc.ABCMeta):
    TYPE = NotImplementedError

    def __init__(self, master=None, alias=None, repo=None):
        self._master = master
        self._repo = repo
        self.current_user = None
        self._uuid = None
        self._users = []
        self._secret = None
        self._alias = alias
        self._last_update = None
        self._session_ttl = settings.SESSION_TTL
        self._shares = None

    @property
    @abc.abstractmethod
    def subtype(self):
        pass

    @property
    def master(self):
        return self._master

    def _get_user(self, user_id):
        for user in self._users:
            if user_id == isinstance(user_id, uuid.UUID) and str(user.uuid) or user.uuid:
                return user

    def get_user(self, user_id: str, alias: str = None):
        user = uuid.UUID(user_id) == self.master.uuid and self.master or self._get_user(user_id)
        return alias is not None and user and user.alias == alias and user or user

    @abc.abstractclassmethod
    def new(cls, master=None, alias=None, repo=None):
        pass

    @property
    def users(self):
        return self._users

    @property
    def ttl(self):
        if not self._last_update:
            raise exceptions.SystemException('the object must be stored first')
        rem = self._session_ttl - (int(time.time()) - self._last_update)
        return self._session_ttl if self._session_ttl == -1 else rem > 0 and rem or 0

    @classmethod
    def get(cls, session_id: str, auth: str=None, repo=secret_share_repository) -> 'SharedSession':
        session = repo.get_session('{}/{}'.format(cls.TYPE, session_id))
        if not session:
            raise exceptions.ObjectNotFoundException
        i = cls.from_dict(session, repo=repo)
        if auth:
            if not i.get_user(auth):
                raise exceptions.ObjectDeniedException
            i.current_user = i.get_user(auth)
        return i

    @abc.abstractclassmethod
    def from_dict(self, session, repo=None) -> 'SharedSession':
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @property
    def uuid(self) -> (None, uuid.UUID):
        return self._uuid

    def store(self) -> 'SharedSession':
        self._last_update = int(time.time())
        res = self._repo.store_session(self.to_dict())
        self._uuid = res['uuid']
        return self

    def update(self) -> 'SharedSession':
        self._last_update = int(time.time())
        self._repo.update_session(self.to_dict())
        return self

    def delete(self) -> bool:
        assert self._uuid
        self._repo.delete_session(self.to_dict())
        return True

    @abc.abstractmethod
    def to_api(self, auth=None):
        pass

    def _get_users_aliases(self) -> dict:
        users = {
            user.alias: [user.ROLE, user.uuid] for user in self._users
        }
        return users

    def join(self, alias: str):
        users = self._get_users_aliases()
        if self._secret and len(users) >= self._secret.shares:
            raise exceptions.DomainObjectBusyException
        if alias in users:
            raise exceptions.ObjectDeniedException
        user = SharedSessionUser(user_id=uuid.uuid4(), alias=alias)
        self._users.append(user)
        return user

    @property
    def secret(self) -> 'SharedSessionSecret':
        return self._secret