import requests


class FXCWebApiService():
    def __init__(self, fxc_webapi_url: str, max_secret_size=1024000):
        self._fxc_webapi_url = fxc_webapi_url
        self._max = max_secret_size
        self._protocol = 'FXC1'
        self._alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        self._type = 'WEB'
        self._entropy = 3.1
        self._length = 6

    def split(self, secret: str, quorum, total) -> list:
        payload = {
            'data': secret,
            'config': {
                'quorum': quorum,
                'total': total,
            }
        }
        print(payload)
        response = requests.post('{}/fxc/v1/secrets'.format(self._fxc_webapi_url), json=payload)
        response.raise_for_status()
        return response.json()['data']

    def combine(self, shares: list, quorum, total) -> str:
        payload = {
            'data': shares,
            'config': {
                'quorum': quorum,
                'total': total,
            }
        }
        print(payload)
        response = requests.put('{}/fxc/v1/secrets'.format(self._fxc_webapi_url), json=payload)
        response.raise_for_status()
        return response.json()['data']