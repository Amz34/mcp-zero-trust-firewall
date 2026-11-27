import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from mcp_firewall.core.telemetry import TelemetryTracker

class TestTelemetry(unittest.TestCase):
    def test_telemetry_reduction_calculation(self):
        tracker = TelemetryTracker()
        raw = {
            "result": {
                "text": "A" * 800,  # ~200 tokens
                "client_guidance": "B" * 1200 # ~300 tokens
            }
        }
        clean = {
            "result": {
                "text": "A" * 800
            }
        }
        tracker.record_turn(raw, clean, was_coerced=False, threats_count=1)
        summary = tracker.get_summary()

        self.assertGreater(summary["tokens_saved"], 0)
        self.assertGreater(summary["token_reduction_pct"], 40.0)
        self.assertEqual(summary["threats_blocked"], 1)

if __name__ == "__main__":
    unittest.main()
