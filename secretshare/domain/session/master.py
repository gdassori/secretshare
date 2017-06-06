import uuid
from uuid import UUID

from secretshare.domain import DomainObject


class ShareSessionMaster(DomainObject):
    def __init__(self, masterkey: UUID=None, alias: str=None):
        self._uuid = masterkey
        self._alias = alias

    @classmethod
    def new(cls, alias=None):
        i = cls(masterkey=str(uuid.uuid4()), alias=alias)
        return i

    def store(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

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
    def from_dict(cls, data: dict) -> 'ShareSessionMaster':
        i = cls()
        i._uuid = UUID(data['uuid'])
        i._alias = data['alias']
        return i