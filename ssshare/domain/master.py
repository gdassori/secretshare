import uuid
from ssshare.domain.user import SharedSessionUser


class SharedSessionMaster(SharedSessionUser):
    def __init__(self, user_id: uuid.UUID = None, alias: str = None, session=None):
        super().__init__(user_id, alias, session)
        self._shareholder = False

    ROLE='master'

    @classmethod
    def new(cls, alias=None):
        i = cls(user_id=str(uuid.uuid4()), alias=alias)
        return i

    @property
    def uuid(self):
        return self._uuid

    @property
    def is_shareholder(self):
        return self._shareholder

    @property
    def alias(self):
        return self._alias

    def to_dict(self) -> dict:
        return dict(
            uuid=str(self._uuid),
            alias=self._alias,
            shareholder=self._shareholder
        )