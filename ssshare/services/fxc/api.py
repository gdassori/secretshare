class FXCWebApiService():
    def __init__(self, fxc_webapi_url: str, max_secret_size=1024000):
        self._fxc_webapi_url = fxc_webapi_url
        self._max = max_secret_size
        self._protocol = 'FXC1'
        self._alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        self._type = 'WEB'
        self._entropy = 3.1
        self._length = 6

    def split(self, secret: 'SharedSessionSecret') -> 'Shares':
        raise NotImplementedError

    def combine(self, shares) -> 'SharedSessionSecret':
        raise NotImplementedError
