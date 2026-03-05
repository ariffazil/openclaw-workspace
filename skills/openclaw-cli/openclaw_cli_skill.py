"""
openclaw-cli skill — read-only OpenClaw CLI diagnostics.

Runs INSIDE the openclaw_gateway container where `openclaw` binary is available.
All commands use --json where supported. No mutating commands.

Floors: F1 (read-only), F2 (truth — report exactly what CLI returns),
        F4 (clarity — structured output), F7 (humility — mark failures explicitly),
        F11 (operator-only), F12 (no injection — args hardcoded).
"""

from __future__ import annotations

import json
import subprocess
from typing import Any, Optional


def _run_openclaw(args: list[str], timeout: int = 15) -> dict[str, Any]:
    """
    Run `openclaw <args>` and return structured result.
    Always returns: {ok, code, data, stderr}
    """
    try:
        result = subprocess.run(
            ["openclaw"] + args,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        ok = result.returncode == 0
        # Try to parse JSON output; fallback to raw text
        data: Any
        try:
            data = json.loads(stdout)
        except (json.JSONDecodeError, ValueError):
            data = stdout if stdout else None

        return {"ok": ok, "code": result.returncode, "data": data, "stderr": stderr or None}
    except FileNotFoundError:
        return {
            "ok": False,
            "code": -1,
            "data": None,
            "stderr": (
                "openclaw binary not found. This skill must run inside the "
                "openclaw_gateway container."
            ),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "data": None, "stderr": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"ok": False, "code": -1, "data": None, "stderr": str(e)}


def openclaw_get_health(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw health --json"""
    return _run_openclaw(["health", "--json"])


def openclaw_get_status(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw status --json --all"""
    return _run_openclaw(["status", "--json", "--all"])


def openclaw_list_models(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw models list --json [--provider <provider>]"""
    args = ["models", "list", "--json"]
    provider: Optional[str] = (params or {}).get("provider")
    if provider:
        args += ["--provider", provider]
    return _run_openclaw(args)


def openclaw_get_models_status(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw models status --json"""
    return _run_openclaw(["models", "status", "--json"])


def openclaw_channels_status(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw channels status --probe --json [--channel <channel>]"""
    args = ["channels", "status", "--probe", "--json"]
    channel: Optional[str] = (params or {}).get("channel")
    if channel:
        args += ["--channel", channel]
    return _run_openclaw(args)


def openclaw_memory_search(params: dict[str, Any]) -> dict[str, Any]:
    """openclaw memory search <query>"""
    query: str = params.get("query", "")
    if not query.strip():
        return {"ok": False, "code": -1, "data": None, "stderr": "query is required"}
    return _run_openclaw(["memory", "search", query])


def openclaw_gateway_status(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """openclaw gateway status --json"""
    return _run_openclaw(["gateway", "status", "--json"])


# Tool dispatch table — maps tool_id → function
TOOL_DISPATCH: dict[str, Any] = {
    "openclaw_get_health": openclaw_get_health,
    "openclaw_get_status": openclaw_get_status,
    "openclaw_list_models": openclaw_list_models,
    "openclaw_get_models_status": openclaw_get_models_status,
    "openclaw_channels_status": openclaw_channels_status,
    "openclaw_memory_search": openclaw_memory_search,
    "openclaw_gateway_status": openclaw_gateway_status,
}


def call(tool_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Entry point for OpenClaw skill runtime."""
    fn = TOOL_DISPATCH.get(tool_id)
    if fn is None:
        return {
            "ok": False,
            "code": -1,
            "data": None,
            "stderr": f"Unknown tool_id: {tool_id!r}. Valid: {list(TOOL_DISPATCH)}",
        }
    return fn(params or {})
