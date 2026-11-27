import sys
import json
import asyncio
import subprocess
from typing import List, Optional
from ..core.config import FirewallConfig
from ..core.sanitizer import PayloadSanitizer
from ..core.coercer import ErrorCoercer
from ..core.telemetry import TelemetryTracker

class StdioInterceptor:
    """
    Spawns an underlying MCP server process (e.g. npx @modelcontextprotocol/server-notion)
    and transparently filters all inbound and outbound JSON-RPC streams over stdio.
    """
    def __init__(self, command: List[str], config: Optional[FirewallConfig] = None):
        self.command = command
        self.config = config or FirewallConfig()
        self.sanitizer = PayloadSanitizer(self.config)
        self.coercer = ErrorCoercer()
        self.telemetry = TelemetryTracker()
        self.process: Optional[asyncio.subprocess.Process] = None

    async def run(self):
        # Spawn target subprocess
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        loop = asyncio.get_event_loop()
        reader_task = asyncio.create_task(self._forward_client_to_server())
        writer_task = asyncio.create_task(self._forward_server_to_client())
        stderr_task = asyncio.create_task(self._forward_stderr())

        await asyncio.gather(reader_task, writer_task, stderr_task)

    async def _forward_client_to_server(self):
        """Forward requests from parent (Claude/Cursor) to MCP server."""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            if self.process and self.process.stdin:
                self.process.stdin.write(line)
                await self.process.stdin.drain()

    async def _forward_server_to_client(self):
        """Intercept responses from MCP server, filter, coerce, and output to client."""
        while True:
            if not self.process or not self.process.stdout:
                break
            line = await self.process.stdout.readline()
            if not line:
                break

            decoded = line.decode("utf-8", errors="ignore").strip()
            if not decoded:
                continue

            try:
                msg = json.loads(decoded)
                was_coerced = False

                # Step 1: Check for paywall / rate-limit coercion
                if self.config.coerce_paywalls_to_429:
                    should_coerce, retry_after = self.coercer.should_coerce(msg)
                    if should_coerce:
                        clean_msg = self.coercer.coerce_to_429(msg, retry_after)
                        was_coerced = True
                        events = [f"Coerced vendor paywall to HTTP 429 machine error (retry: {retry_after}s)"]
                    else:
                        clean_msg, events = self.sanitizer.sanitize(msg)
                else:
                    clean_msg, events = self.sanitizer.sanitize(msg)

                # Record Telemetry
                self.telemetry.record_turn(msg, clean_msg, was_coerced, len(events))

                # Write sanitized message to stdout
                out_bytes = (json.dumps(clean_msg) + "\n").encode("utf-8")
                sys.stdout.buffer.write(out_bytes)
                sys.stdout.buffer.flush()

            except json.JSONDecodeError:
                # Raw text line / non-JSON passthrough
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()

    async def _forward_stderr(self):
        """Pass stderr logs directly."""
        while True:
            if not self.process or not self.process.stderr:
                break
            line = await self.process.stderr.readline()
            if not line:
                break
            sys.stderr.buffer.write(line)
            sys.stderr.buffer.flush()
