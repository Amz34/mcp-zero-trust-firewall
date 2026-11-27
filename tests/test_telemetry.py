import pytest
from mcp_firewall.core.telemetry import TelemetryTracker

def test_telemetry_reduction_calculation():
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

    assert summary["tokens_saved"] > 0
    assert summary["token_reduction_pct"] > 40.0
    assert summary["threats_blocked"] == 1
