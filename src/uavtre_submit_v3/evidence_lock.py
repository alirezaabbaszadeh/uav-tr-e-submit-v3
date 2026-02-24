from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class EvidenceLockResult:
    passed: bool
    campaign_dir: Path
    required_files: list[str]
    missing_files: list[str]
    files: list[dict[str, object]]


def lock_evidence(*, campaign_dir: Path, out_json: Path) -> EvidenceLockResult:
    """Lock a campaign by hashing the minimal metadata files.

    This does not modify the evidence. It only records a digest for traceability.
    """

    required = [
        "CAMPAIGN_MANIFEST.json",
        "RUN_PLAN.json",
        "ENV_SNAPSHOT.json",
        "COMMAND_LOG.csv",
    ]

    missing = [name for name in required if not (campaign_dir / name).exists()]

    files: list[dict[str, object]] = []
    for name in required:
        p = campaign_dir / name
        if not p.exists():
            continue
        files.append(
            {
                "name": name,
                "path": p.as_posix(),
                "bytes": p.stat().st_size,
                "sha256": _sha256(p),
            }
        )

    payload = {
        "campaign_dir": campaign_dir.as_posix(),
        "required_files": required,
        "missing_files": missing,
        "files": files,
        "passed": len(missing) == 0,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return EvidenceLockResult(
        passed=payload["passed"],
        campaign_dir=campaign_dir,
        required_files=required,
        missing_files=missing,
        files=files,
    )
