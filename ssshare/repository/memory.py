from uuid import uuid4
from ssshare.repository.abstract import Repository


class VolatileRepository(Repository):
    def __init__(self, storage):
        self._storage = storage

    def get_session(self, session_id: str):
        data = self._storage.get(session_id)
        return data or None

    def store_session(self, data: dict):
        session_id = data.get('session_id', str(uuid4()))
        assert not self._storage.get(session_id)
        data['uuid'] = session_id
        self._storage[session_id] = data
        return data

    def update_session(self, data: dict):
        assert self.get_session(data['uuid'])
        self._storage[data['uuid']] = data
        return data

    def delete_session(self, data: dict):
        self.get_session(data['uuid'])
        del self._storage[data['uuid']]
