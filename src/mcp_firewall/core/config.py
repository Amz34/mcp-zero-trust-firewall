from pydantic import BaseModel, Field
from typing import List, Set

class FirewallConfig(BaseModel):
    """Configuration for Zero-Trust MCP Firewall."""
    strict_schema_enforcement: bool = Field(
        default=True,
        description="Drop non-standard metadata keys returned by MCP servers (e.g. client_guidance)"
    )
    banned_keys: Set[str] = Field(
        default_factory=lambda: {
            "client_guidance",
            "prompt_guidance",
            "upsell_prompt",
            "system_instruction",
            "assistant_directive",
            "override_prompt",
            "vendor_guidance",
            "injected_instruction"
        },
        description="Keys to strip recursively from JSON-RPC responses"
    )
    strip_upsell_patterns: bool = Field(
        default=True,
        description="Redact promotional upsell and marketing copy from error payloads"
    )
    coerce_paywalls_to_429: bool = Field(
        default=True,
        description="Coerce rate-limit/paywall marketing errors to clean JSON-RPC 429 machine codes"
    )
    enable_telemetry: bool = Field(
        default=True,
        description="Calculate token tax savings and telemetry metrics per session"
    )
    redaction_placeholder: str = Field(
        default="[REDACTED_PROMOTIONAL_INJECTION]",
        description="String placeholder used to replace injected text"
    )
