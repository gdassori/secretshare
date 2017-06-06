from uuid import uuid4
from secretshare import exceptions
from secretshare.repository.abstract import SecretShareRepository


class SecretShareMemoryRepository(SecretShareRepository):
    def __init__(self, storage):
        self._storage = storage

    def get_session(self, session_id: str):
        data = self._storage.get(session_id)
        if not data:
            raise exceptions.ObjectNotFoundException
        return data

    def store_session(self, data: dict):
        session_id = str(uuid4())
        assert not self._storage.get(session_id)
        data['uuid'] = session_id
        self._storage[session_id] = data
        return data

    def update_session(self, data: dict):
        data = self.get_session(data['uuid'])
        self._storage[data['uuid']] = data
        return data

    def delete_session(self, data: dict):
        self.get_session(data['uuid'])
        del self._storage[data['uuid']]
