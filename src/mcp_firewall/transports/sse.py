import sys
import json
from typing import Dict, Any
from ..core.config import FirewallConfig
from ..core.sanitizer import PayloadSanitizer
from ..core.coercer import ErrorCoercer

class SSEReverseProxy:
    """
    HTTP/SSE Remote Proxy for networked MCP endpoints (e.g. https://mcp.notion.com).
    Intercepts JSON-RPC payloads in flight over SSE streams.
    """
    def __init__(self, config: FirewallConfig = None):
        self.config = config or FirewallConfig()
        self.sanitizer = PayloadSanitizer(self.config)
        self.coercer = ErrorCoercer()

    def filter_event(self, event_data: str) -> str:
        """Processes and filters a single SSE event data payload."""
        if not event_data.strip():
            return event_data
        try:
            msg = json.loads(event_data)
            if self.config.coerce_paywalls_to_429:
                should_coerce, retry_after = self.coercer.should_coerce(msg)
                if should_coerce:
                    return json.dumps(self.coercer.coerce_to_429(msg, retry_after))
            clean_msg, _ = self.sanitizer.sanitize(msg)
            return json.dumps(clean_msg)
        except Exception:
            return event_data
