from uuid import UUID
from secretshare.domain import DomainObject
from secretshare.ioc import secret_share_repository


class ShareSession(DomainObject):
    def __init__(self, repo=secret_share_repository):
        self._repo = repo
        self._uuid = None

    def get(self) -> 'ShareSession':
        pass

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'ShareSession':
        i = cls(repo=repo)
        i._uuid = data['uuid']
        return i

    @property
    def uuid(self) -> (None, UUID):
        return self._uuid

    def store(self):
        assert not self._uuid
        self._repo.store_session(self)

    def update(self):
        assert self._uuid
        self._repo.update_session(self)

    def delete(self):
        assert self._uuid
        self._repo.delete_session(self)