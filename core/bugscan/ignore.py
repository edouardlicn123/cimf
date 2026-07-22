"""`.bugscanignore` 解析器"""

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IgnoreRule:
    file_pattern: str
    line: int | None = None
    pattern_id: str | None = None


@dataclass
class IgnoreParser:
    rules: list[IgnoreRule] = field(default_factory=list)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return
        for raw in path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            comment_pos = stripped.find("#")
            if comment_pos >= 0:
                stripped = stripped[:comment_pos].strip()
            if not stripped:
                continue
            parts = stripped.split(":")
            file_pattern = parts[0]
            line: int | None = None
            pattern_id: str | None = None
            if len(parts) >= 2:
                try:
                    line = int(parts[1])
                except ValueError:
                    pattern_id = parts[1]
            if len(parts) >= 3:
                pattern_id = parts[2]
            self.rules.append(IgnoreRule(file_pattern=file_pattern, line=line, pattern_id=pattern_id))

    def is_ignored(self, file: str, line: int, pattern_id: str) -> bool:
        for rule in self.rules:
            if not fnmatch.fnmatch(file, rule.file_pattern):
                continue
            if rule.line is not None and rule.line != line:
                continue
            if rule.pattern_id is not None and rule.pattern_id != pattern_id:
                continue
            return True
        return False
