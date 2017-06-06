import abc


class SecretShareRepository(metaclass=abc.ABCMeta):

    def get_session(self, data: dict) -> dict:
        pass

    def store_session(self, data: dict) -> dict:
        pass

    def update_session(self, data: dict) -> dict:
        pass

    def delete_session(self, data: dict) -> dict:
        pass
