"""
Thread-Safe Tamper-Evident Audit Logging Module for INDUSAI-X.
SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Features:
- Thread-safe append-only JSON-Lines logging via re-entrant lock (threading.RLock()).
- Strictly increasing monotonic sequence IDs (sequence_id) ensuring deterministic order.
- SHA-256 cryptographic hash chaining (prev_hash -> entry_hash).
- verify_audit_trail() verification function detecting any historical line tampering,
  deletion, or re-ordering.
"""

import os
import json
import hashlib
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List


GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


class AuditLogger:
    """Thread-safe, append-only tamper-evident audit logger."""

    def __init__(self, log_file_path: str = "audit_trail.jsonl"):
        self.log_file_path = log_file_path
        self._lock = threading.RLock()
        self._last_sequence_id = -1
        self._last_hash = GENESIS_HASH

        os.makedirs(os.path.dirname(os.path.abspath(log_file_path)), exist_ok=True)
        self._initialize_from_existing_log()

    def _initialize_from_existing_log(self) -> None:
        """Inspects existing log file to determine current sequence_id and head hash."""
        with self._lock:
            if not os.path.exists(self.log_file_path) or os.path.getsize(self.log_file_path) == 0:
                self._last_sequence_id = -1
                self._last_hash = GENESIS_HASH
                return

            last_line = ""
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        last_line = line.strip()

            if last_line:
                try:
                    data = json.loads(last_line)
                    self._last_sequence_id = data.get("sequence_id", -1)
                    self._last_hash = data.get("entry_hash", GENESIS_HASH)
                except Exception:
                    # If corrupted, start from -1
                    pass

    @staticmethod
    def _compute_hash(
        sequence_id: int,
        prev_hash: str,
        timestamp_utc: str,
        actor_id: str,
        role: str,
        action: str,
        resource: str,
        status: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Computes deterministic SHA-256 hash across all canonical log fields."""
        payload = {
            "sequence_id": sequence_id,
            "prev_hash": prev_hash,
            "timestamp_utc": timestamp_utc,
            "actor_id": actor_id,
            "role": role,
            "action": action,
            "resource": resource,
            "status": status,
            "metadata": metadata
        }
        canonical_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def log(
        self,
        actor_id: str,
        role: str,
        action: str,
        resource: str,
        status: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Thread-safely appends an audit record with monotonic sequence and hash chaining.
        """
        if metadata is None:
            metadata = {}

        timestamp_utc = datetime.now(timezone.utc).isoformat()

        with self._lock:
            seq_id = self._last_sequence_id + 1
            prev_hash = self._last_hash
            entry_hash = self._compute_hash(
                sequence_id=seq_id,
                prev_hash=prev_hash,
                timestamp_utc=timestamp_utc,
                actor_id=actor_id,
                role=role,
                action=action,
                resource=resource,
                status=status,
                metadata=metadata
            )

            entry = {
                "sequence_id": seq_id,
                "timestamp_utc": timestamp_utc,
                "actor_id": actor_id,
                "role": role,
                "action": action,
                "resource": resource,
                "status": status,
                "metadata": metadata,
                "prev_hash": prev_hash,
                "entry_hash": entry_hash
            }

            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            self._last_sequence_id = seq_id
            self._last_hash = entry_hash
            return entry

    @classmethod
    def verify_audit_trail(cls, log_file_path: str) -> Tuple[bool, Optional[int], str]:
        """
        Verifies the cryptographic integrity of the entire audit trail log.
        Returns:
            (is_valid: bool, corrupted_line_index: Optional[int], message: str)
        """
        if not os.path.exists(log_file_path):
            return True, None, "Log file does not exist (empty log is trivially valid)."

        expected_prev_hash = GENESIS_HASH
        expected_seq_id = 0

        with open(log_file_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line_str = line.strip()
                if not line_str:
                    continue

                try:
                    entry = json.loads(line_str)
                except Exception as e:
                    return False, line_idx, f"Invalid JSON format on line {line_idx}: {str(e)}"

                # 1. Monotonic sequence check
                actual_seq_id = entry.get("sequence_id")
                if actual_seq_id != expected_seq_id:
                    return False, line_idx, (
                        f"Sequence ID mismatch on line {line_idx}: "
                        f"expected {expected_seq_id}, found {actual_seq_id}"
                    )

                # 2. Previous Hash chain check
                actual_prev_hash = entry.get("prev_hash")
                if actual_prev_hash != expected_prev_hash:
                    return False, line_idx, (
                        f"Hash chain broken on line {line_idx}: "
                        f"expected prev_hash {expected_prev_hash}, found {actual_prev_hash}"
                    )

                # 3. Recompute and verify entry hash
                computed_hash = cls._compute_hash(
                    sequence_id=entry["sequence_id"],
                    prev_hash=entry["prev_hash"],
                    timestamp_utc=entry["timestamp_utc"],
                    actor_id=entry["actor_id"],
                    role=entry["role"],
                    action=entry["action"],
                    resource=entry["resource"],
                    status=entry["status"],
                    metadata=entry.get("metadata", {})
                )

                if computed_hash != entry.get("entry_hash"):
                    return False, line_idx, (
                        f"Tampering detected on line {line_idx}: "
                        f"entry_hash does not match recomputed SHA-256 payload"
                    )

                expected_prev_hash = entry["entry_hash"]
                expected_seq_id += 1

        return True, None, f"Audit trail verified successfully ({expected_seq_id} entries valid)."
