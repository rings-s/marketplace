import json
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in SKIP_PATHS or request.url.path.startswith("/ws"):
            return await call_next(request)

        response = await call_next(request)
        locale = getattr(request.state, "locale", "ar")
        request_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

        if response.headers.get("content-type", "").startswith("application/json"):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            try:
                data = json.loads(body)
            except Exception:
                return response

            # Already wrapped (e.g. from exception handler)
            if isinstance(data, dict) and "success" in data:
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json",
                )

            if response.status_code >= 400:
                wrapped = {
                    "success": False,
                    "error": {
                        "code": _status_to_code(response.status_code),
                        "message_ar": data.get("detail", "حدث خطأ"),
                        "message_en": data.get("detail", "An error occurred"),
                    },
                    "meta": {"request_id": request_id, "locale": locale},
                }
            else:
                wrapped = {
                    "success": True,
                    "data": data,
                    "meta": {"request_id": request_id, "locale": locale},
                }

            wrapped_body = json.dumps(wrapped, ensure_ascii=False).encode()
            new_headers = dict(response.headers)
            new_headers["content-length"] = str(len(wrapped_body))
            return Response(
                content=wrapped_body,
                status_code=response.status_code,
                headers=new_headers,
                media_type="application/json",
            )

        return response


def _status_to_code(status: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        402: "PAYMENT_REQUIRED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
    }.get(status, "ERROR")
