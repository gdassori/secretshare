from ssshare.repository.memory import VolatileRepository
from ssshare.services.fxc.api import FXCWebApiService
from ssshare.settings import FXC_API_URL


secret_share_repository = VolatileRepository(storage=dict())
fxc_web_api_service = FXCWebApiService(FXC_API_URL)