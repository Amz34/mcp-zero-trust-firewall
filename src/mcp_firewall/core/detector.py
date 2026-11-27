import re
from typing import List, Tuple
from pydantic import BaseModel

class InjectionDetectionResult(BaseModel):
    is_injected: bool
    confidence_score: float
    matched_patterns: List[str]
    threat_category: str

class PromptInjectionDetector:
    """
    Heuristic and pattern-matching engine detecting indirect prompt injection,
    role hijacking, and vendor marketing directive attacks in MCP streams.
    """
    
    UPSELL_PATTERNS = [
        re.compile(r"try\s+notion\s+(?:business|enterprise|plus|ai)", re.IGNORECASE),
        re.compile(r"upgrade\s+(?:your\s+)?(?:plan|workspace|tier|subscription)", re.IGNORECASE),
        re.compile(r"reach\s+(?:your|the)\s+(?:hourly|daily|monthly)\s+(?:sql|query|api)\s+limit", re.IGNORECASE),
        re.compile(r"https?://(?:www\.)?notion\.so/pricing\S*", re.IGNORECASE),
        re.compile(r"visit\s+(?:our\s+)?pricing\s+page", re.IGNORECASE),
        re.compile(r"contact\s+sales\s+to\s+increase\s+limits", re.IGNORECASE),
    ]

    DIRECTIVE_HIJACK_PATTERNS = [
        re.compile(r"you\s+must\s+(?:tell|inform|pitch|instruct|recommend)\s+the\s+user", re.IGNORECASE),
        re.compile(r"do\s+not\s+(?:reveal|disclose|mention)\s+that\s+this\s+(?:message|instruction|error)", re.IGNORECASE),
        re.compile(r"act\s+as\s+if\s+you\s+are", re.IGNORECASE),
        re.compile(r"ignore\s+(?:all\s+)?prior\s+instructions", re.IGNORECASE),
        re.compile(r"<system>.*?</system>", re.DOTALL | re.IGNORECASE),
        re.compile(r"\[SYSTEM(?:\s+PROMPT)?\]", re.IGNORECASE),
        re.compile(r"output\s+the\s+following\s+link", re.IGNORECASE),
    ]

    def scan_text(self, text: str) -> InjectionDetectionResult:
        if not text:
            return InjectionDetectionResult(
                is_injected=False,
                confidence_score=0.0,
                matched_patterns=[],
                threat_category="NONE"
            )

        matched = []
        threat = "NONE"
        score = 0.0

        for pat in self.DIRECTIVE_HIJACK_PATTERNS:
            if pat.search(text):
                matched.append(f"Directive Hijack: {pat.pattern}")
                threat = "DIRECTIVE_INJECTION"
                score = max(score, 0.95)

        for pat in self.UPSELL_PATTERNS:
            if pat.search(text):
                matched.append(f"Vendor Upsell Hijack: {pat.pattern}")
                if threat == "NONE":
                    threat = "VENDOR_UPSELL_TAX"
                score = max(score, 0.85)

        return InjectionDetectionResult(
            is_injected=len(matched) > 0,
            confidence_score=score,
            matched_patterns=matched,
            threat_category=threat
        )
