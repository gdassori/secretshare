import uuid
from ssshare.domain.user import SharedSessionUser


class SharedSessionMaster(SharedSessionUser):
    ROLE='master'

    @classmethod
    def new(cls, alias=None):
        i = cls(user_id=str(uuid.uuid4()), alias=alias)
        i._shareholder = False
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
            alias=self._alias,
            shareholder=self._shareholder
        )