import logging

import httpx
from fastapi import HTTPException, Request, Response, status

logger = logging.getLogger(__name__)

_http_client = httpx.AsyncClient(timeout=30.0)


async def proxy_request(request: Request, target_url: str, service_name: str) -> Response:
    excluded = {"host", "content-length"}
    forwarded_headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded}

    query_string = request.url.query
    full_url = f"{target_url}?{query_string}" if query_string else target_url
    body = await request.body()

    try:
        upstream = await _http_client.request(
            method=request.method, url=full_url,
            headers=forwarded_headers, content=body,
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{service_name} is unavailable.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"{service_name} timed out.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Gateway error with {service_name}.")

    return Response(
        content=upstream.content, status_code=upstream.status_code,
        headers=dict(upstream.headers), media_type=upstream.headers.get("content-type"),
    )
