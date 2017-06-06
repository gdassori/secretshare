import uuid
from uuid import UUID
from ssshare.domain.user import ShareSessionUser


class ShareSessionMaster(ShareSessionUser):
    ROLE='master'

    def __init__(self, user_id: UUID=None, alias: str=None):
        super().__init__(user_id=user_id, alias=alias)

    @classmethod
    def new(cls, alias=None):
        i = cls(user_id=str(uuid.uuid4()), alias=alias)
        return i

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

    def to_api(self, auth=None):
        res = dict(
            alias=self._alias,
            role=self.ROLE
        )
        if auth:
            pass
        return res