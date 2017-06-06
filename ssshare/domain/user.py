from uuid import UUID
from ssshare.domain import DomainObject


class ShareSessionUser(DomainObject):
    ROLE = 'user'

    def __init__(self, user_id: UUID = None, alias: str = None):
        self._uuid = user_id
        self._alias = alias


    @property
    def uuid(self):
        return self._uuid

    @property
    def alias(self):
        return self._alias

    def to_dict(self) -> dict:
        return dict(
            uuid=str(self._uuid),
            alias=self._alias
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'ShareSessionUser':
        i = cls()
        i._uuid = UUID(data['uuid'])
        i._alias = data['alias']
        return i