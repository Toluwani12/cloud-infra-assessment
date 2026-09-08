"""Configuration checks need no AWS account or internet access."""
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from config import load_config


class ConfigTests(unittest.TestCase):
    def load(self, **settings):
        config = {"endpoints": [{"url": "https://example.com"}], **settings}
        with patch.dict(os.environ, {"HEALTHCHECK_CONFIG": json.dumps(config)}):
            return load_config("unused.json")

    def test_defaults_and_environment_override(self):
        config = self.load()
        self.assertEqual(config["attempts"], 3)
        self.assertEqual(config["endpoints"][0]["expected_status"], 200)

    def test_example_file(self):
        with patch.dict(os.environ, {}, clear=True):
            config = load_config(Path(__file__).with_name("endpoints.json"))
        self.assertEqual(len(config["endpoints"]), 2)

    def test_invalid_settings(self):
        for settings in ({"attempts": 0}, {"attempts": 1.5}, {"timeout": 0},
                         {"backoff": -1}, {"timeout": float("inf")},
                         {"attempts": True}, {"endpoints": []},
                         {"endpoints": [{"url": "file:///etc/hosts"}]},
                         {"endpoints": [{"url": "https://user:secret@example.com"}]},
                         {"endpoints": [{"url": "https://example.com", "expected_status": True}]}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.load(**settings)
