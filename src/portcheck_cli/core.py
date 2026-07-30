"""Core TCP connectivity check for portcheck-cli.

This module checks a single host:port at a time. It is a diagnostic
building block, not a scanner — there is deliberately no support for
ranges, sweeps, or multiple targets in one call.
"""
from __future__ import annotations

import socket
from dataclasses import dataclass

DEFAULT_TIMEOUT = 2.0
MIN_PORT = 1
MAX_PORT = 65535


@dataclass
class PortCheckResult:
    status: str  # "open", "closed", or "error"
    message: str


def parse_target(target: str) -> tuple[str, int]:
    """Split a `host:port` string into (host, port), validating the port.

    Uses the rightmost colon as the separator so bracketed IPv6 addresses
    (e.g. `[::1]:8080`) and plain hostnames both work.
    """
    if ":" not in target:
        raise ValueError(f"target must be in host:port form, got {target!r}")
    host, _, port_text = target.rpartition(":")
    host = host.strip("[]")
    if not host:
        raise ValueError(f"target must be in host:port form, got {target!r}")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError(f"invalid port {port_text!r}") from exc
    if not (MIN_PORT <= port <= MAX_PORT):
        raise ValueError(f"port {port} out of range ({MIN_PORT}-{MAX_PORT})")
    return host, port


def check_port(host: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> PortCheckResult:
    """Attempt a single TCP connection to host:port and report the outcome."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return PortCheckResult("open", f"{host}:{port} is open")
    except socket.gaierror as exc:
        return PortCheckResult("error", f"could not resolve host {host!r}: {exc}")
    except (TimeoutError, socket.timeout):
        return PortCheckResult("closed", f"{host}:{port} timed out after {timeout}s")
    except ConnectionRefusedError:
        return PortCheckResult("closed", f"{host}:{port} refused the connection")
    except OSError as exc:
        return PortCheckResult("error", f"{host}:{port}: {exc}")
