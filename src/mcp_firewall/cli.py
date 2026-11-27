import sys
import os
import json
import argparse
import asyncio

try:
    from .core.config import FirewallConfig
    from .core.detector import PromptInjectionDetector
    from .core.sanitizer import PayloadSanitizer
    from .core.coercer import ErrorCoercer
    from .core.telemetry import TelemetryTracker
    from .transports.stdio import StdioInterceptor
except (ImportError, ValueError):
    # Support direct execution
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from mcp_firewall.core.config import FirewallConfig
    from mcp_firewall.core.detector import PromptInjectionDetector
    from mcp_firewall.core.sanitizer import PayloadSanitizer
    from mcp_firewall.core.coercer import ErrorCoercer
    from mcp_firewall.core.telemetry import TelemetryTracker
    from mcp_firewall.transports.stdio import StdioInterceptor

def main():
    parser = argparse.ArgumentParser(
        prog="mcp-firewall",
        description="Enterprise Zero-Trust MCP Proxy & Prompt Injection Firewall"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # Command: run (Wrap another MCP command over stdio)
    run_parser = subparsers.add_parser("run", help="Wrap an MCP server command with zero-trust sanitization")
    run_parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Target command to run (e.g. npx -y @modelcontextprotocol/server-notion)")

    # Command: test-payload (Sanitize a JSON string or file directly)
    test_parser = subparsers.add_parser("sanitize", help="Sanitize a raw JSON payload string or stdin")
    test_parser.add_argument("--json", type=str, help="Raw JSON string")

    # Command: audit (Scan text for prompt injection patterns)
    audit_parser = subparsers.add_parser("scan", help="Scan a text block for prompt injection and upsell hijack")
    audit_parser.add_argument("--text", type=str, required=True, help="Text to inspect")

    args = parser.parse_args()

    if args.subcommand == "scan":
        detector = PromptInjectionDetector()
        res = detector.scan_text(args.text)
        print(json.dumps(res.model_dump(), indent=2))

    elif args.subcommand == "sanitize":
        config = FirewallConfig()
        sanitizer = PayloadSanitizer(config)
        coercer = ErrorCoercer()

        raw_text = args.json if args.json else sys.stdin.read()
        try:
            msg = json.loads(raw_text)
            should_coerce, retry = coercer.should_coerce(msg)
            if should_coerce:
                out = coercer.coerce_to_429(msg, retry)
            else:
                out, events = sanitizer.sanitize(msg)
            print(json.dumps(out, indent=2))
        except Exception as e:
            sys.stderr.write(f"Error parsing JSON: {e}\n")
            sys.exit(1)

    elif args.subcommand == "run":
        if not args.cmd:
            parser.error("No command specified to run. Example: mcp-firewall run -- npx -y @modelcontextprotocol/server-notion")
        cmd = args.cmd
        if cmd[0] == "--":
            cmd = cmd[1:]
        interceptor = StdioInterceptor(cmd)
        asyncio.run(interceptor.run())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
