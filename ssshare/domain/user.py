import uuid
from ssshare.domain import DomainObject


class SharedSessionUser(DomainObject):
    ROLE = 'user'

    def __init__(self, user_id: uuid.UUID = None, alias: str = None, session=None):
        self._uuid = user_id
        self._alias = alias
        self._session = session

    @property
    def is_master(self):
        return self.ROLE == 'master'

    @property
    def uuid(self):
        return self._uuid

    @property
    def session(self):
        return self._session

    @property
    def alias(self):
        return self._alias

    def to_dict(self) -> dict:
        return dict(
            uuid=str(self._uuid),
            alias=self._alias
        )

    @classmethod
    def from_dict(cls, data: dict, session=None) -> 'SharedSessionUser':
        i = cls(session=session)
        i._uuid = uuid.UUID(data['uuid'])
        i._alias = data['alias']
        return i

    def to_api(self, auth=None):
        res = dict(
            alias=self._alias,
            role=self.ROLE
        )
        if self._is_auth_valid(auth):
            res['key'] = str(self.uuid)
        return res

    def _is_auth_valid(self, auth: str):
        if auth == str(self._uuid):
            return True
        if self.session and self.session.master and str(self.session.master.uuid) == auth:
            return True
