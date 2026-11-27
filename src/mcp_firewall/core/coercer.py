import re
from typing import Any, Dict, Optional, Tuple

class ErrorCoercer:
    """
    Coerces conversational paywall/rate-limit prompts into standard,
    deterministic JSON-RPC 2.0 error codes (HTTP 429 Machine Error).
    """

    RATE_LIMIT_CUES = [
        re.compile(r"hourly\s+(?:sql|query|api)\s+limit", re.IGNORECASE),
        re.compile(r"rate\s+limit\s+exceeded", re.IGNORECASE),
        re.compile(r"too\s+many\s+requests", re.IGNORECASE),
        re.compile(r"quota\s+exhausted", re.IGNORECASE),
        re.compile(r"upgrade\s+to\s+increase\s+limits", re.IGNORECASE),
    ]

    def should_coerce(self, message: Dict[str, Any]) -> Tuple[bool, Optional[int]]:
        """
        Inspects message to determine if it is a vendor paywall disguise.
        Returns: (should_coerce, retry_after_seconds)
        """
        # Case 1: Message is an error object
        error = message.get("error")
        if error:
            msg = str(error.get("message", "")) + " " + str(error.get("data", ""))
            for cue in self.RATE_LIMIT_CUES:
                if cue.search(msg):
                    return True, 3600

        # Case 2: Message is a result object containing paywall text disguised as success
        result = message.get("result")
        if isinstance(result, dict):
            content = str(result.get("content", ""))
            for cue in self.RATE_LIMIT_CUES:
                if cue.search(content):
                    return True, 3600

        return False, None

    def coerce_to_429(self, original_msg: Dict[str, Any], retry_after: int = 3600) -> Dict[str, Any]:
        """
        Constructs standard JSON-RPC 2.0 429 machine-readable error envelope.
        Eliminates LLM confusion and prompts deterministic exponential backoff.
        """
        msg_id = original_msg.get("id")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32029,  # Standard JSON-RPC custom server error: 429 Rate Limit
                "message": "UPSTREAM_RATE_LIMIT_EXCEEDED: Workspace API quota reached.",
                "data": {
                    "http_status": 429,
                    "retry_after_seconds": retry_after,
                    "backoff_recommended": True,
                    "sanitized_by": "MCP-Zero-Trust-Firewall"
                }
            }
        }
