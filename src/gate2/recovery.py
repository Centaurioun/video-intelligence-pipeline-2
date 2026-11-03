"""Synthetic, fail-closed recovery apparatus for the Gate 2 experiment.

This module is deliberately an apparatus around an externally authoritative
journal.  The checkpoint below records measurements and replay position only;
it never mirrors the journal's operation records.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class RecoveryRefusal(RuntimeError):
    """Raised when an apparatus checkpoint or bound identity is unsafe."""


@dataclass(frozen=True)
class RecoveryBinding:
    f01_sha: str
    c04_sha: str
    e05_sha: str
    workload_digest: str
    configuration_digest: str
    previous_manifest_digest: str
    current_manifest_digest: str
    generation_id: str
    semantic_space_id: str
    receipt_identity: str

    def __post_init__(self) -> None:
        for name in ("f01_sha", "c04_sha", "e05_sha", "workload_digest",
                     "configuration_digest", "previous_manifest_digest",
                     "current_manifest_digest"):
            value = getattr(self, name)
            permitted_lengths = (40, 64) if name.endswith("_sha") else (64,)
            if not isinstance(value, str) or len(value) not in permitted_lengths or any(
                c not in "0123456789abcdef" for c in value
            ):
                expected = ("a lowercase 40-hex git SHA-1 or 64-hex SHA-256 digest"
                            if permitted_lengths == (40, 64)
                            else "a lowercase 64-hex SHA-256 digest")
                raise ValueError(f"{name} must be {expected}")
        for name in ("generation_id", "semantic_space_id", "receipt_identity"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be a non-empty identity")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _binding_digest(binding: RecoveryBinding) -> str:
    return hashlib.sha256(_canonical(asdict(binding))).hexdigest()


def _seal(payload: dict[str, Any]) -> dict[str, Any]:
    return {"payload": payload, "integrity_sha256": hashlib.sha256(_canonical(payload)).hexdigest()}


def _write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _canonical(_seal(payload)) + b"\n"
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _new_payload(binding: RecoveryBinding) -> dict[str, Any]:
    return {
        "schema": "synthetic-recovery-apparatus-v1",
        "binding_sha256": _binding_digest(binding),
        "attempt": 0,
        "checkpoint": 0,
        "pre_state_digest": None,
        "post_state_digest": None,
        "operation_count": 0,
        "completed_count": 0,
        "crash_consumed": False,
        "last_crash_point": None,
    }


def _read_checkpoint(path: Path, binding: RecoveryBinding) -> dict[str, Any]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        payload = envelope["payload"]
        integrity = envelope["integrity_sha256"]
        if not isinstance(payload, dict) or hashlib.sha256(_canonical(payload)).hexdigest() != integrity:
            raise ValueError("integrity mismatch")
        required = {"schema", "binding_sha256", "attempt", "checkpoint", "pre_state_digest",
                    "post_state_digest", "operation_count", "completed_count", "crash_consumed",
                    "last_crash_point"}
        if set(payload) != required or payload["schema"] != "synthetic-recovery-apparatus-v1":
            raise ValueError("partial or unknown apparatus checkpoint")
        if payload["binding_sha256"] != _binding_digest(binding):
            raise ValueError("stale recovery binding")
        for key in ("attempt", "checkpoint", "operation_count", "completed_count"):
            if type(payload[key]) is not int or payload[key] < 0:
                raise ValueError("invalid measurement")
        if type(payload["crash_consumed"]) is not bool:
            raise ValueError("invalid crash measurement")
        return payload
    except RecoveryRefusal:
        raise
    except Exception as exc:
        raise RecoveryRefusal(f"invalid recovery apparatus checkpoint: {exc}") from exc


class RecoveryHarness:
    def __init__(self, checkpoint_path: Path, binding: RecoveryBinding, adapter: Any,
                 payload: dict[str, Any]):
        self.checkpoint_path = checkpoint_path
        self.binding = binding
        self.adapter = adapter
        self._payload = payload

    @classmethod
    def open(cls, checkpoint_path: str | os.PathLike[str], binding: RecoveryBinding, adapter: Any) -> "RecoveryHarness":
        path = Path(checkpoint_path)
        if path.exists():
            payload = _read_checkpoint(path, binding)
        else:
            payload = _new_payload(binding)
            _write_checkpoint(path, payload)
        return cls(path, binding, adapter, payload)

    def _save(self) -> None:
        _write_checkpoint(self.checkpoint_path, self._payload)

    def run(self, crash_point: str | None = None) -> dict[str, Any]:
        if crash_point not in (None, "before_action", "after_side_effect_before_completion"):
            raise ValueError("unsupported synthetic crash point")
        # Receipt validation is deliberately the first adapter operation.
        if not self.adapter.validate_receipt(self.binding.receipt_identity):
            raise RecoveryRefusal("E05 receipt identity was refused")
        self.adapter.reconcile_sqlite_tail()
        pre_digest = self.adapter.state_digest()
        self._payload["attempt"] += 1
        self._payload["pre_state_digest"] = pre_digest
        self._save()
        operation_ids = tuple(self.adapter.start_or_resume(self.binding))
        self._payload["operation_count"] = len(operation_ids)
        self._payload["checkpoint"] += 1
        self._save()

        injected = False
        for operation_id in operation_ids:
            if self.adapter.is_complete(operation_id):
                continue
            if crash_point == "before_action" and not self._payload["crash_consumed"] and not injected:
                self._payload["crash_consumed"] = True
                self._payload["last_crash_point"] = crash_point
                self._payload["checkpoint"] += 1
                self._save()
                raise RuntimeError("synthetic crash before action")
            self.adapter.apply_idempotent(operation_id)
            if crash_point == "after_side_effect_before_completion" and not self._payload["crash_consumed"] and not injected:
                self._payload["crash_consumed"] = True
                self._payload["last_crash_point"] = crash_point
                self._payload["checkpoint"] += 1
                self._payload["post_state_digest"] = self.adapter.state_digest()
                self._save()
                raise RuntimeError("synthetic crash after side effect before completion")
            self.adapter.mark_complete(operation_id)
            self._payload["completed_count"] += 1
            self._payload["checkpoint"] += 1
            self._save()
            injected = True

        post_digest = self.adapter.state_digest()
        self._payload["post_state_digest"] = post_digest
        self._payload["completed_count"] = len(operation_ids)
        self._payload["checkpoint"] += 1
        self._save()
        return {
            "attempts": self._payload["attempt"],
            "checkpoints": self._payload["checkpoint"],
            "operation_count": len(operation_ids),
            "pre_state_digest": pre_digest,
            "post_state_digest": post_digest,
            "NOT_OBSERVED": {
                "archive reliability": "NOT_OBSERVED",
                "archive scale": "NOT_OBSERVED",
                "wall clock": "NOT_OBSERVED",
                "protected media": "NOT_OBSERVED",
                "provider/model behavior": "NOT_OBSERVED",
            },
        }
