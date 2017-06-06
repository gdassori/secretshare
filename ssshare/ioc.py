from ssshare.repository.memory import VolatileRepository


secret_share_repository = VolatileRepository(storage=dict())