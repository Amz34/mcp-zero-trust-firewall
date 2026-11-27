import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from mcp_firewall.core.coercer import ErrorCoercer

class TestCoercer(unittest.TestCase):
    def test_coerce_paywall_disguised_error(self):
        coercer = ErrorCoercer()
        payload = {
            "jsonrpc": "2.0",
            "id": 42,
            "error": {
                "message": "You have reached your hourly query limit. Upgrade to increase limits."
            }
        }
        should, retry = coercer.should_coerce(payload)
        self.assertTrue(should)
        self.assertEqual(retry, 3600)
        self.assertIsNotNone(retry)
        assert retry is not None

        coerced = coercer.coerce_to_429(payload, retry)
        self.assertEqual(coerced["id"], 42)
        self.assertEqual(coerced["error"]["code"], -32029)
        self.assertEqual(coerced["error"]["data"]["http_status"], 429)
        self.assertEqual(coerced["error"]["data"]["retry_after_seconds"], 3600)

    def test_ignore_normal_errors(self):
        coercer = ErrorCoercer()
        payload = {
            "jsonrpc": "2.0",
            "id": 10,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }
        should, _ = coercer.should_coerce(payload)
        self.assertFalse(should)

if __name__ == "__main__":
    unittest.main()
