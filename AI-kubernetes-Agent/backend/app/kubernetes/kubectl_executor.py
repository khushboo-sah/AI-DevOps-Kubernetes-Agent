"""Utilities for executing kubectl commands safely."""

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Sequence

from loguru import logger

from app.core.config import get_settings
from app.kubernetes.kind_docker import resolve_api_server


@dataclass(frozen=True)
class KubectlResult:
    """Structured result from a kubectl command."""

    command: list[str]
    stdout: str
    stderr: str
    return_code: int
    success: bool
    timed_out: bool = False

    @property
    def error_message(self) -> str:
        """Return the most useful error text for failed commands."""

        if self.timed_out:
            return "kubectl command timed out"

        return self.stderr.strip() or self.stdout.strip() or "kubectl command failed"


class KubectlExecutor:
    """Small wrapper around subprocess for kubectl calls."""

    def __init__(
        self,
        context: str | None = None,
        default_timeout_seconds: int = 30,
    ) -> None:
        self.context = context
        self.default_timeout_seconds = default_timeout_seconds

    def run(
        self,
        args: Sequence[str],
        timeout_seconds: int | None = None,
    ) -> KubectlResult:
        """Run a kubectl command and return captured output.

        Args should not include the leading ``kubectl`` binary.
        """

        command = self._build_command(args)
        timeout = timeout_seconds or self.default_timeout_seconds
        safe_command = shlex.join(command)
        logger.info("Running kubectl command: {}", safe_command)

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            logger.error("kubectl binary was not found")
            return KubectlResult(
                command=command,
                stdout="",
                stderr="kubectl binary was not found",
                return_code=127,
                success=False,
            )
        except subprocess.TimeoutExpired as exc:
            logger.error("kubectl command timed out after {} seconds", timeout)
            return KubectlResult(
                command=command,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                return_code=124,
                success=False,
                timed_out=True,
            )

        success = completed.returncode == 0
        if success:
            logger.info("kubectl command succeeded: {}", safe_command)
        else:
            logger.warning(
                "kubectl command failed with code {}: {}",
                completed.returncode,
                safe_command,
            )

        return KubectlResult(
            command=command,
            stdout=completed.stdout,
            stderr=completed.stderr,
            return_code=completed.returncode,
            success=success,
        )

    def run_json(
        self,
        args: Sequence[str],
        timeout_seconds: int | None = None,
    ) -> tuple[KubectlResult, dict[str, Any] | None]:
        """Run kubectl and parse stdout as JSON when the command succeeds."""

        result = self.run(args, timeout_seconds=timeout_seconds)
        if not result.success:
            return result, None

        try:
            return result, json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse kubectl JSON output: {}", exc)
            return (
                KubectlResult(
                    command=result.command,
                    stdout=result.stdout,
                    stderr=f"Failed to parse kubectl JSON output: {exc}",
                    return_code=1,
                    success=False,
                ),
                None,
            )

    def _build_command(self, args: Sequence[str]) -> list[str]:
        settings = get_settings()
        command = ["kubectl"]

        kubeconfig = settings.kubeconfig_path or os.getenv("KUBECONFIG")
        if kubeconfig:
            command.extend(["--kubeconfig", kubeconfig])

        if self.context:
            command.extend(["--context", self.context])
            api_server = resolve_api_server(self.context)
            if api_server:
                logger.info(
                    "Using kind Docker network API server {} for context {}",
                    api_server,
                    self.context,
                )
                command.extend(["--server", api_server])
                if os.getenv("KUBE_INSECURE_SKIP_TLS", "").lower() in {
                    "1",
                    "true",
                    "yes",
                }:
                    command.append("--insecure-skip-tls-verify")

        command.extend(args)
        return command
