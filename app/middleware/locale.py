from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

SUPPORTED_LOCALES = {"ar", "en"}
DEFAULT_LOCALE = "ar"


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        accept_lang = request.headers.get("Accept-Language", DEFAULT_LOCALE)
        locale = accept_lang.split(",")[0].split("-")[0].strip().lower()
        if locale not in SUPPORTED_LOCALES:
            locale = DEFAULT_LOCALE
        request.state.locale = locale
        response = await call_next(request)
        response.headers["Content-Language"] = locale
        return response
