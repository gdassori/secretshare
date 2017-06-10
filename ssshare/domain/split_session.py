from ssshare.domain.master import SharedSessionMaster
from ssshare.domain.session import SharedSession
from ssshare.control import secret_share_repository


class SplitSession(SharedSession):
    def __init__(self, master: SharedSessionMaster=None, alias=None, repo=secret_share_repository):
        super().__init__(master=master, alias=alias, repo=repo)

    @classmethod
    def new(cls, master=None, alias=None, repo=secret_share_repository):
        i = cls(master=master, alias=alias, repo=repo)
        return i

    def to_dict(self) -> dict:
        return dict(
            uuid=self._uuid,
            master=self._master.to_dict(),
            last_update=self._last_update,
            alias=self._alias,
            users=[u.to_dict() for u in self.users],
            secret=self._secret and self._secret.to_dict()
        )

    @classmethod
    def from_dict(cls, data: dict, repo=secret_share_repository) -> 'SplitSession':
        from ssshare.domain.master import SharedSessionMaster
        from ssshare.domain.user import SharedSessionUser
        from ssshare.domain.secret import SharedSessionSecret
        i = cls(repo=repo)
        i._uuid = data['uuid']
        i._master = data.get('master') and SharedSessionMaster.from_dict(data['master'], session=i)
        i._last_update = data['last_update']
        i._alias = data['alias']
        i._users = {u['uuid']: SharedSessionUser.from_dict(u, session=i) for u in data['users']}
        i._secret = data['secret'] and SharedSessionSecret.from_dict(data['secret'])
        return i

    def to_api(self, auth=None):
        users = [self.master.to_api(auth=auth)] + [user.to_api(auth=auth) for user in self.users]
        res = {
            'ttl': self.ttl,
            'users': users,
            'secret_sha256': self._secret and self._secret.sha256,
            'alias': self._alias
        }
        if auth and self.master and auth == str(self.master.uuid):
            res['secret'] = self._secret and self._secret.secret
        return res

    def set_secret_from_payload(self, payload: dict):
        from ssshare.domain.secret import SharedSessionSecret
        self._secret = SharedSessionSecret.from_dict(payload['session']['secret'])
        return self._secret