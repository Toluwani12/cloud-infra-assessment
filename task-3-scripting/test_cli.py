"""Exercise the complete command against a real local HTTP server."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response({"/ok": 200, "/missing": 404, "/redirect": 302}.get(self.path, 503))
        self.send_header("Location", "/ok")
        self.end_headers()

    def log_message(self, *args):
        pass


class CommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def run_command(self, endpoints):
        base = f"http://127.0.0.1:{self.server.server_port}"
        config = {"attempts": 2, "backoff": 0, "timeout": 1,
                  "endpoints": [{"url": base + path, "expected_status": status}
                                for path, status in endpoints]}
        process = subprocess.run([sys.executable, str(Path(__file__).with_name("healthcheck.py"))],
                                 env={**os.environ, "HEALTHCHECK_CONFIG": json.dumps(config)},
                                 capture_output=True, text=True, timeout=10)
        return process.returncode, json.loads(process.stdout)

    def test_success_including_expected_404_and_redirect(self):
        code, report = self.run_command([("/ok", 200), ("/missing", 404), ("/redirect", 302)])
        self.assertEqual(code, 0)
        self.assertTrue(report["passed"])
        self.assertTrue(all(result["response_time_ms"] >= 0 for result in report["results"]))

    def test_failure_still_checks_remaining_endpoints(self):
        code, report = self.run_command([("/bad", 200), ("/ok", 200)])
        self.assertEqual(code, 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(len(report["results"][0]["attempts"]), 2)
        self.assertTrue(report["results"][1]["passed"])

    def test_invalid_configuration_has_distinct_exit(self):
        code, report = self.run_command([])
        self.assertEqual(code, 2)
        self.assertIn("error", report)
