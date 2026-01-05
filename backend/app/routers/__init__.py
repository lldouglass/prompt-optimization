from .logs import router as logs_router
from .admin import router as admin_router
from .requests import router as requests_router
from .agents import router as agents_router
from .billing import router as billing_router
from .auth import router as auth_router
from .referral import router as referral_router
from .optimize_ws import router as optimize_ws_router
from .media_optimize_ws import router as media_optimize_ws_router

__all__ = ["logs_router", "admin_router", "requests_router", "agents_router", "billing_router", "auth_router", "referral_router", "optimize_ws_router", "media_optimize_ws_router"]
