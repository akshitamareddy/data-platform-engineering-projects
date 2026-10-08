# Data Platform Engineering Portfolio

Three beginner-friendly, practical Python data infrastructure projects:

1. **Automated Log Parsing Pipeline** — parses Nginx combined logs, including an optional trailing `$request_time` field, and writes status/latency data to PostgreSQL. `--follow` processes appended lines (restart if the log rotates).
2. **API Performance Monitor** — repeatedly checks two public API endpoints, stores response time and errors, and prints threshold alerts. You can add one custom endpoint with `MONITOR_URL`.
3. **Infrastructure Cost Optimizer** — joins summarized cloud billing CSV rows with utilization CSV metrics and flags potentially underutilized compute/databases. Percentages are illustrative, not guaranteed actual savings. Do not terminate resources automatically.

## Quick start

You need Python 3.10+, Docker Compose and an internet connection for API probes and first-time dependencies.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
docker compose up -d
```

From the project root, in separate terminal sessions:

```bash
python -m log_pipeline.main --file samples/access.log
python -m api_monitor.main --once
python -m api_monitor.main --interval 60 --threshold-ms 1500
python -m cost_optimizer.main --billing samples/billing.csv --utilization samples/utilization.csv
python -m unittest discover -s tests -v
```

The demo PostgreSQL credentials are local-development only. To use another database set `DATABASE_URL` in your shell. PostgreSQL data remains in a Docker volume. Avoid committing production passwords or sensitive log data.

## Example metrics queries

```sql
-- Hourly error ratio
SELECT date_trunc('hour', observed_at) AS hour,
       COUNT(*) AS requests,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status_code >= 500) / NULLIF(COUNT(*),0), 2) AS error_pct
FROM nginx_requests
GROUP BY 1 ORDER BY 1;

-- Average latency and error ratio by endpoint
SELECT target, COUNT(*) AS checks,
       ROUND(AVG(latency_ms)::numeric, 1) AS avg_latency_ms,
       ROUND(100.0 * AVG(is_error::int), 1) AS error_pct
FROM api_checks GROUP BY 1;
```

To connect to local PostgreSQL:

```bash
docker compose exec postgres psql -U platform -d observability
```

## Nginx configuration

The usual combined Nginx access log does **not** contain response time. To capture it, define a log format with `$request_time` (seconds):

```nginx
log_format timed_combined '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time';
access_log /var/log/nginx/access.log timed_combined;
```

For production: add offset tracking or a queue for at-least-once delivery, deduplication, batched inserts, structured JSON logs, secret management, API authentication/rate-limit handling, rolling failure-rate alerts and notification sinks. The sample monitor emits alerts only to the terminal; it is not a hosted alerting service. AWS CUR raw files require a preprocessing step because column naming differs from the simplified demonstration billing export.

## Tech stack
Python, regex, Requests, PostgreSQL, Docker Compose, CSV, unittest.
