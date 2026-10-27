"""Invoke an external live-model adapter over a JSON stdin/stdout protocol."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from typing import Any


def command_parts(command: str) -> list[str]:
    parts = shlex.split(command, posix=os.name != "nt")
    if os.name == "nt":
        parts = [item[1:-1] if len(item) >= 2 and item[0] == item[-1] and item[0] in {"'", '"'} else item for item in parts]
    if not parts:
        raise ValueError("Runner command is empty")
    return parts


def run_command(command: str, request: dict[str, Any], timeout: float = 300.0) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        command_parts(command),
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    if completed.returncode != 0:
        raise RuntimeError(f"Runner failed ({completed.returncode}): {completed.stderr.strip()}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"Runner returned invalid JSON: {error}") from error
    if not isinstance(result, dict):
        raise ValueError("Runner response must be a JSON object")
    result.setdefault("metadata", {})
    if not isinstance(result["metadata"], dict):
        raise ValueError("Runner metadata must be a JSON object")
    result["metadata"].setdefault("wall_latency_ms", elapsed_ms)
    tokens = result["metadata"].setdefault("tokens", {})
    if not isinstance(tokens, dict):
        raise ValueError("Runner metadata.tokens must be an object")
    for key in ("input", "output", "total"):
        tokens.setdefault(key, None)
    result["metadata"].setdefault("token_source", "unavailable" if tokens["total"] is None else "runner")
    return result
