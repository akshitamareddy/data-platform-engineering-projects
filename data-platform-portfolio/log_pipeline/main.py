"""Parse Nginx combined-access logs and persist structured events to PostgreSQL.

Usage: python -m log_pipeline.main --file samples/access.log
       python -m log_pipeline.main --file /var/log/nginx/access.log --follow
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import os
import re
import time
from pathlib import Path

# Nginx: '$remote_addr - $remote_user [$time_local] "$request" '
#        '$status $body_bytes_sent "$http_referer" "$http_user_agent" '
#        '$request_time'  # Set request_time in nginx.conf for real response times.
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\d{3}) (?P<bytes>\d+|-) '
    r'"[^"]*" "[^"]*"(?: (?P<duration>\d+(?:\.\d+)?|-))?$'
)

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS nginx_requests (
 id BIGSERIAL PRIMARY KEY,
 observed_at TIMESTAMPTZ NOT NULL,
 remote_addr TEXT NOT NULL,
 method TEXT,
 path TEXT,
 status_code INTEGER NOT NULL,
 bytes_sent BIGINT,
 response_time_ms DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_nginx_observed ON nginx_requests(observed_at);
CREATE INDEX IF NOT EXISTS idx_nginx_status ON nginx_requests(status_code);
"""


def parse_line(line: str) -> dict | None:
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    parts = match['request'].split(' ', 2)
    timestamp = datetime.strptime(match['time'], '%d/%b/%Y:%H:%M:%S %z')
    duration = match['duration']
    return {
        'observed_at': timestamp.astimezone(timezone.utc),
        'remote_addr': match['ip'],
        'method': parts[0] if len(parts) >= 2 else None,
        'path': parts[1] if len(parts) >= 2 else None,
        'status_code': int(match['status']),
        'bytes_sent': int(match['bytes']) if match['bytes'] != '-' else None,
        'response_time_ms': float(duration) * 1000 if duration and duration != '-' else None,
    }


def lines_from_file(path: Path, follow: bool):
    with path.open('r', encoding='utf-8') as stream:
        while True:
            line = stream.readline()
            if line:
                yield line
            elif not follow:
                return
            else:
                time.sleep(0.5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, type=Path)
    parser.add_argument('--follow', action='store_true', help='Stream appended log lines (Ctrl+C to stop)')
    args = parser.parse_args()
    import psycopg
    dsn = os.getenv('DATABASE_URL', 'postgresql://platform:platform_dev_only@localhost:5432/observability')
    with psycopg.connect(dsn) as conn:
        conn.execute(CREATE_SQL)
        count, rejected = 0, 0
        try:
            for line in lines_from_file(args.file, args.follow):
                event = parse_line(line)
                if event is None:
                    rejected += 1
                    print(f'Skipping malformed line #{count + rejected}')
                    continue
                conn.execute('''
                    INSERT INTO nginx_requests (observed_at, remote_addr, method, path,
                                                status_code, bytes_sent, response_time_ms)
                    VALUES (%(observed_at)s, %(remote_addr)s, %(method)s, %(path)s,
                            %(status_code)s, %(bytes_sent)s, %(response_time_ms)s)
                ''', event)
                conn.commit()
                count += 1
                print(f"ingested status={event['status_code']} duration_ms={event['response_time_ms']}")
        except KeyboardInterrupt:
            print('Stopped following log.')
        finally:
            print(f'Inserted {count} rows, rejected {rejected} lines')

if __name__ == '__main__':
    main()
