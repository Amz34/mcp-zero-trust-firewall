import pytest
from mcp_firewall.core.coercer import ErrorCoercer

def test_coerce_paywall_disguised_error():
    coercer = ErrorCoercer()
    payload = {
        "jsonrpc": "2.0",
        "id": 42,
        "error": {
            "message": "You have reached your hourly query limit. Upgrade to increase limits."
        }
    }
    should, retry = coercer.should_coerce(payload)
    assert should is True
    assert retry == 3600

    coerced = coercer.coerce_to_429(payload, retry)
    assert coerced["id"] == 42
    assert coerced["error"]["code"] == -32029
    assert coerced["error"]["data"]["http_status"] == 429
    assert coerced["error"]["data"]["retry_after_seconds"] == 3600

def test_ignore_normal_errors():
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
    assert should is False
