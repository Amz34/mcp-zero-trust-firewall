from typing import Any, Dict, List, Tuple
from .config import FirewallConfig
from .detector import PromptInjectionDetector, InjectionDetectionResult

class PayloadSanitizer:
    """
    Zero-trust JSON-RPC recursive schema sanitizer.
    Strips dangerous metadata keys, redacts prompt injections, and preserves typed data.
    """
    def __init__(self, config: FirewallConfig = None):
        self.config = config or FirewallConfig()
        self.detector = PromptInjectionDetector()

    def sanitize(self, payload: Any) -> Tuple[Any, List[str]]:
        """
        Recursively traverses and cleanses payload.
        Returns: (sanitized_payload, list_of_redaction_events)
        """
        events = []
        cleaned = self._traverse(payload, events)
        return cleaned, events

    def _traverse(self, node: Any, events: List[str]) -> Any:
        if isinstance(node, dict):
            clean_dict = {}
            for k, v in node.items():
                k_lower = k.lower()
                # Check for banned guidance keys
                if self.config.strict_schema_enforcement and k_lower in self.config.banned_keys:
                    events.append(f"Dropped banned directive key: '{k}'")
                    continue
                clean_dict[k] = self._traverse(v, events)
            return clean_dict

        elif isinstance(node, list):
            return [self._traverse(item, events) for item in node]

        elif isinstance(node, str):
            # Check string content for prompt injections or upsell tax
            if self.config.strip_upsell_patterns:
                scan = self.detector.scan_text(node)
                if scan.is_injected:
                    events.append(f"Sanitized text (Threat: {scan.threat_category}): {scan.matched_patterns[0]}")
                    # Clean the string
                    sanitized_str = node
                    for pat in self.detector.DIRECTIVE_HIJACK_PATTERNS + self.detector.UPSELL_PATTERNS:
                        sanitized_str = pat.sub(self.config.redaction_placeholder, sanitized_str)
                    return sanitized_str
            return node

        return node
