import uuid
from ssshare.domain import DomainObject


class SharedSessionUser(DomainObject):
    ROLE = 'user'

    def __init__(self, user_id: uuid.UUID = None, alias: str = None, session=None):
        self._uuid = user_id
        self._alias = alias
        self._session = session
        self._shareholder = True

    @property
    def is_master(self):
        return self.ROLE == 'master'

    @property
    def is_shareholder(self):
        return self._shareholder

    @property
    def uuid(self):
        return self._uuid

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        value.current_user = self

    @property
    def alias(self):
        return self._alias

    def to_dict(self) -> dict:
        return dict(
            uuid=str(self._uuid),
            alias=self._alias,
            shareholder=self._shareholder
        )

    @classmethod
    def from_dict(cls, data: dict, session=None) -> 'SharedSessionUser':
        i = cls(session=session)
        i._uuid = uuid.UUID(data['uuid'])
        i._alias = data['alias']
        i._shareholder = data['shareholder']
        return i

    def to_api(self, auth=None):
        res = dict(
            alias=self._alias,
            role=self.ROLE
        )
        if self.ROLE == 'master':
            res['shareholder'] = self._shareholder

        if self._is_auth_valid(auth):
            res['auth'] = str(self.uuid)
            secret = self.session and self.session.secret or None
            if secret and secret.splitted:
                share = secret.get_share(self)
                if share:
                    res['share'] = share.value
        return res

    def _is_auth_valid(self, auth: str):
        if auth == str(self._uuid):
            return True
        if self.session and self.session.master and str(self.session.master.uuid) == auth:
            return True
