from uuid import uuid4
from ssshare.repository.abstract import Repository


class VolatileRepository(Repository):
    def __init__(self, storage):
        self._storage = storage

    def get_session(self, key: str):
        data = self._storage.get(key)
        return data or None

    def store_session(self, data: dict):
        session_id = data.get('session_id', str(uuid4()))
        k = '{}/{}'.format(data['type'], session_id)
        assert not self.get_session(k)
        data['uuid'] = session_id
        self._storage[k] = data
        return data

    def update_session(self, data: dict):
        k = '{}/{}'.format(data['type'], data['uuid'])
        assert self.get_session(k)
        self._storage[k] = data
        return data

    def delete_session(self, data: dict):
        k = '{}/{}'.format(data['type'], data['uuid'])
        self.get_session(k)
        del self._storage[k]
