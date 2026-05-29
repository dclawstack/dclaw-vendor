"""Observability: structured logging + Prometheus metrics (V8.3).

- ``setup_logging`` configures structlog for JSON (prod) or console (dev) output —
  the app logs through structlog, never ``print``.
- ``PrometheusMiddleware`` records request count + latency per method/route/status.
- ``metrics_endpoint`` exposes them in Prometheus text format at ``/metrics``.
"""

from __future__ import annotations

import logging
import time

import structlog
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "path"],
)


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.app_env != "dev"
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


log = structlog.get_logger("dclaw_vendor")


def _route_template(request: Request) -> str:
    """Use the matched route path (templated) to keep label cardinality bounded."""
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        path = _route_template(request)
        elapsed = time.perf_counter() - start
        REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response


async def metrics_endpoint(request: Request) -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
