"""Sample HTTP APIs at an interval; persist measurements and warn on failures/latency.

Usage: python -m api_monitor.main --once
       python -m api_monitor.main --interval 60 --threshold-ms 1500
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import os
import time
import requests

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS api_checks (
 id BIGSERIAL PRIMARY KEY,
 checked_at TIMESTAMPTZ NOT NULL,
 target TEXT NOT NULL,
 status_code INTEGER,
 latency_ms DOUBLE PRECISION NOT NULL,
 is_error BOOLEAN NOT NULL,
 error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_api_checks_target_time ON api_checks(target, checked_at);
"""
DEFAULT_ENDPOINTS = {
    'github': 'https://api.github.com/rate_limit',
    'httpbin': 'https://httpbin.org/status/200',
}


def probe(session: requests.Session, target: str, url: str, threshold_ms: float) -> dict:
    start = time.perf_counter()
    status, message = None, None
    try:
        response = session.get(url, timeout=8, headers={'Accept': 'application/json'})
        status = response.status_code
        if status >= 400:
            message = f'HTTP {status}'
    except requests.RequestException as exc:
        message = str(exc)
    latency = (time.perf_counter() - start) * 1000
    is_error = message is not None
    if is_error or latency > threshold_ms:
        print(f"ALERT {target}: status={status}, latency={latency:.0f}ms, problem={message or 'slow response'}")
    return {
        'checked_at': datetime.now(timezone.utc),
        'target': target,
        'status_code': status,
        'latency_ms': latency,
        'is_error': is_error,
        'error_message': message,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--interval', type=float, default=60)
    parser.add_argument('--threshold-ms', type=float, default=1500)
    args = parser.parse_args()
    if args.interval <= 0 or args.threshold_ms <= 0:
        parser.error('--interval and --threshold-ms must be positive')
    import psycopg
    dsn = os.getenv('DATABASE_URL', 'postgresql://platform:platform_dev_only@localhost:5432/observability')
    endpoints = dict(DEFAULT_ENDPOINTS)
    if os.getenv('MONITOR_URL'):
        endpoints['custom'] = os.environ['MONITOR_URL']
    with psycopg.connect(dsn) as conn, requests.Session() as session:
        conn.execute(CREATE_SQL)
        try:
            while True:
                for target, url in endpoints.items():
                    result = probe(session, target, url, args.threshold_ms)
                    conn.execute('''
                        INSERT INTO api_checks (checked_at, target, status_code, latency_ms, is_error, error_message)
                        VALUES (%(checked_at)s, %(target)s, %(status_code)s, %(latency_ms)s, %(is_error)s, %(error_message)s)
                    ''', result)
                    conn.commit()
                    print(f"{target}: status={result['status_code']} latency={result['latency_ms']:.0f}ms")
                if args.once:
                    break
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print('Monitor stopped')

if __name__ == '__main__':
    main()
