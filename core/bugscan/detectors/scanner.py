import ast
from pathlib import Path

from core.bugscan.detectors.finding import SCAN_DIRS, Finding
from core.bugscan.detectors.l1_detectors import L1_DETECTORS
from core.bugscan.detectors.l2_detectors import L2_DETECTORS


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []

    if path.suffix != ".py":
        return findings

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: S110 — file read failure, skip
        return findings

    for _pid, detector in L1_DETECTORS:
        try:  # noqa: SIM105
            findings.extend(detector(path))
        except Exception:  # noqa: S110 — detector failure skip
            pass

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    for _pid, detector in L2_DETECTORS:
        try:  # noqa: SIM105
            findings.extend(detector(path, tree))
        except Exception:  # noqa: S110 — detector failure skip
            pass

    return findings


def scan_all() -> list[Finding]:
    findings: list[Finding] = []
    scanned = 0
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for f in sorted(scan_dir.rglob("*.py")):
            if "/migrations/" in str(f) or "/__pycache__/" in str(f):
                continue
            scanned += 1
            findings.extend(scan_file(f))
    return findings
