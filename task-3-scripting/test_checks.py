"""Check retry decisions without waiting between attempts."""
import unittest
from http.client import BadStatusLine
from unittest.mock import patch

from checks import check_endpoint, request_once


class RetryTests(unittest.TestCase):
    def run_check(self, statuses):
        responses = [{"status_code": status, "response_time_ms": 1, "error": None}
                     for status in statuses]
        with patch("checks.request_once", side_effect=responses), patch("checks.time.sleep") as sleep:
            result = check_endpoint({"url": "http://example.com", "expected_status": 200},
                                    {"attempts": 3, "timeout": 1, "backoff": 2})
        return result, sleep

    def test_success_does_not_retry(self):
        result, sleep = self.run_check([200])
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["attempts"]), 1)
        sleep.assert_not_called()

    def test_recovery_and_increasing_backoff(self):
        result, sleep = self.run_check([503, 503, 200])
        self.assertTrue(result["passed"])
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 4])

    def test_exhausted_retries(self):
        result, sleep = self.run_check([503, 503, 503])
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["attempts"]), 3)
        self.assertEqual(sleep.call_count, 2)

    def test_timeout_is_reported(self):
        with patch("checks.urllib.request.OpenerDirector.open", side_effect=TimeoutError("timed out")):
            result = request_once("http://example.com", 1)
        self.assertIsNone(result["status_code"])
        self.assertIn("timed out", result["error"])

    def test_malformed_http_is_reported(self):
        with patch("checks.urllib.request.OpenerDirector.open", side_effect=BadStatusLine("broken")):
            result = request_once("http://example.com", 1)
        self.assertIsNone(result["status_code"])
        self.assertIn("broken", result["error"])
