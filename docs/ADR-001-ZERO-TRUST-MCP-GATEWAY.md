# Architecture Decision Record (ADR-001)

## Title
Zero-Trust MCP Proxy & Prompt Injection Firewall Architecture

## Status
**APPROVED**

## Context
Commercial hosted Model Context Protocol (MCP) servers (notably Notion's remote endpoints) have been observed embedding unauthorized natural language instructions, promotional upsell copy ("Try Notion Business"), and behavioral directives into tool response streams and error payloads (`client_guidance`).

Because LLMs treat tool responses as authoritative execution context, direct connection to unvalidated remote MCP endpoints creates:
1. **Indirect Prompt Injection & Role Hijacking**: Third-party servers steer agent behavior mid-task.
2. **Context Tax ("Nano-Theft")**: Users pay out-of-pocket for tokens wasted on unsolicited vendor marketing copy.
3. **Agent Confusion & Failure Loops**: Unstructured promotional errors prevent deterministic programmatic retries.

## Decision
All agentic interactions with remote MCP servers MUST route through an inline **Zero-Trust MCP Firewall**. The firewall enforces:
1. **Recursive AST/JSON Schema Sanitization**: Strips non-standard control keys (`client_guidance`, `system_directive`).
2. **Deterministic Error Coercion**: Intercepts vendor paywall traps and normalizes them to JSON-RPC 2.0 `-32029` (HTTP 429) machine codes.
3. **Telemetry & Real-Time Token Auditing**: Emits exact before/after token savings and security breach receipts.

## Consequences
- **Positive**: Eliminates 100% of vendor prompt injection vectors; saves 70-85% of error tokens; enables deterministic agent backoff.
- **Overhead**: Adds an undetectable sub-0.05 ms latency overhead per JSON-RPC frame.
