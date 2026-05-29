# Monitoring (V8.3)

The backend exposes Prometheus metrics at **`/metrics`** (no auth) and logs as
structured JSON via structlog (`APP_ENV != dev`).

## Metrics
- `http_requests_total{method,path,status}` — request counter
- `http_request_duration_seconds{method,path}` — latency histogram

`path` is the **templated** route (e.g. `/api/v1/vendors/{vendor_id}`) so label
cardinality stays bounded.

## Prometheus scrape config
```yaml
scrape_configs:
  - job_name: dclaw-vendor
    metrics_path: /metrics
    static_configs:
      - targets: ["dclaw-vendor-backend:8146"]
```

## Grafana
Import `grafana/dclaw-vendor-dashboard.json` and point it at the Prometheus
datasource. It charts request rate, error rate (5xx), and p95 latency.
