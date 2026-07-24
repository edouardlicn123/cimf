from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    file: str
    line: int
    column: int
    severity: str
    pattern_id: str
    code: str
    message: str
    fix_hint: str


SCAN_DIRS = [
    Path(__file__).parent.parent.parent,  # core/
    Path(__file__).parent.parent.parent.parent / "modules",  # modules/
    Path(__file__).parent.parent.parent.parent / "cimf_django",  # cimf_django/
]

NON_DJANGO_SAVE_CALLERS = frozenset({"wb", "img", "image", "result", "watermarked"})
LINE_CACHE: dict[str, list[str]] = {}


def _get_lines(path: Path) -> list[str]:
    if str(path) not in LINE_CACHE:
        LINE_CACHE[str(path)] = path.read_text(encoding="utf-8").splitlines()
    return LINE_CACHE[str(path)]


def _source_snippet(path: Path, lineno: int, context: int = 1) -> str:
    lines = _get_lines(path)
    start = max(0, lineno - 1 - context)
    end = min(len(lines), lineno - 1 + context + 1)
    return "\n".join(lines[start:end])
