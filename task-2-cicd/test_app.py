import unittest

from app import response_for


class AppTests(unittest.TestCase):
    def test_home(self):
        status, body = response_for("/")
        self.assertEqual(status, 200)
        self.assertEqual(
            body["message"],
            "Welcome to my cloud assessment",
        )

    def test_health(self):
        status, body = response_for("/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_missing_page(self):
        status, body = response_for("/missing")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "Not found")


if __name__ == "__main__":
    unittest.main()