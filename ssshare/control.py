from ssshare.repository.memory import VolatileRepository
from ssshare.services.fxc.api import FXCWebApiSevice
from ssshare.settings import FXC_API_URL


secret_share_repository = VolatileRepository(storage=dict())
fxc_web_api_service = FXCWebApiSevice(FXC_API_URL)