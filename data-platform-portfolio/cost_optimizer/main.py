"""Compare simplified AWS CUR-style CSV billing with utilization metrics.

Expects rows with resource_id,service,monthly_cost_usd and matching
resource_id,cpu_avg_pct,connections_avg in utilization CSV.
This is a demonstration heuristic, not a safe-to-delete determination.
"""
from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from pathlib import Path


def analyze(billing_file: Path, utilization_file: Path) -> list[dict]:
    metrics = {}
    with utilization_file.open(newline='', encoding='utf-8-sig') as handle:
        for row in csv.DictReader(handle):
            metrics[row['resource_id']] = row
    summed = defaultdict(float)
    services = {}
    with billing_file.open(newline='', encoding='utf-8-sig') as handle:
        for row in csv.DictReader(handle):
            rid = row['resource_id']
            summed[rid] += float(row['monthly_cost_usd'])
            services[rid] = row['service'].strip().lower()
    findings = []
    for rid, cost in summed.items():
        metric = metrics.get(rid)
        if not metric:
            continue  # Missing utilization is unknown, never assumed idle.
        service = services[rid]
        cpu = float(metric['cpu_avg_pct'])
        connections = float(metric.get('connections_avg') or 0)
        reason, savings_rate = None, 0.0
        if service in {'rds', 'database'} and cpu < 5 and connections < 1:
            reason, savings_rate = 'Review possibly idle database (CPU <5%, connections <1)', 0.5
        elif service in {'ec2', 'compute'} and cpu < 10:
            reason, savings_rate = 'Review low-CPU compute for downsizing (CPU <10%)', 0.3
        if reason:
            findings.append({
                'resource_id': rid, 'service': service, 'monthly_cost': round(cost, 2),
                'cpu_avg_pct': cpu, 'reason': reason,
                'illustrative_savings': round(cost * savings_rate, 2),
            })
    return sorted(findings, key=lambda item: item['illustrative_savings'], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--billing', type=Path, default=Path('samples/billing.csv'))
    parser.add_argument('--utilization', type=Path, default=Path('samples/utilization.csv'))
    args = parser.parse_args()
    findings = analyze(args.billing, args.utilization)
    if not findings:
        print('No resources matched the review thresholds.')
    for item in findings:
        print(f"{item['resource_id']} [{item['service']}] ${item['monthly_cost']:.2f}/month | "
              f"CPU {item['cpu_avg_pct']}% | illustrative savings ${item['illustrative_savings']:.2f}/month")
        print(f"  {item['reason']}")
    print(f"Illustrative total possible savings: ${sum(x['illustrative_savings'] for x in findings):.2f}/month")
    print('Estimate only: verify workload, right-sizing, storage, reservations and actual pricing before action.')

if __name__ == '__main__':
    main()
