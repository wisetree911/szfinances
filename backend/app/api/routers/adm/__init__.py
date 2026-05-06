from .analytics import router as analytics_router
from .portfolios import router as portfolios_router
from .tbank import router as tbank_router
from .trades import router as trades_router
from .users import router as users_router

routers = [
    users_router,
    portfolios_router,
    trades_router,
    analytics_router,
    tbank_router,
]
