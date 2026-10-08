import tempfile
import unittest
from pathlib import Path
from log_pipeline.main import parse_line
from cost_optimizer.main import analyze

class ProjectsTest(unittest.TestCase):
    def test_nginx_parse(self):
        row = ('203.0.113.10 - - [07/Oct/2026:10:11:12 -0500] '
               '"GET /api/users HTTP/1.1" 200 527 "-" "curl/8.0" 0.045')
        event = parse_line(row)
        self.assertEqual(event['status_code'], 200)
        self.assertEqual(event['response_time_ms'], 45)
        self.assertEqual(event['path'], '/api/users')

    def test_malformed_log(self):
        self.assertIsNone(parse_line('not a log'))

    def test_cost_analysis(self):
        results = analyze(Path('samples/billing.csv'), Path('samples/utilization.csv'))
        self.assertEqual([r['resource_id'] for r in results], ['db-a', 'instance-a'])
        self.assertEqual(sum(r['illustrative_savings'] for r in results), 345.0)

if __name__ == '__main__':
    unittest.main()
