import re
from pathlib import Path

from core.bugscan.detectors.finding import Finding, _source_snippet


def detect_datetime_now(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"datetime\.now\(\)", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="high",
                pattern_id="datetime_now",
                code=_source_snippet(path, lineno),
                message="datetime.now() 缺少时区参数，应使用 timezone.now()",
                fix_hint="from django.utils import timezone → timezone.now()",
            )
        )
    return findings


def detect_jsonfield_default(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"JSONField\(.*?default\s*=\s*(\{|\[)", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="critical",
                pattern_id="jsonfield_default",
                code=_source_snippet(path, lineno),
                message="JSONField 使用可变默认值，所有实例将共享同一对象",
                fix_hint="改为 default=dict 或 default=list（无括号）",
            )
        )
    return findings


def detect_nullbooleanfield(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"NullBooleanField\(", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="medium",
                pattern_id="nullbooleanfield",
                code=_source_snippet(path, lineno),
                message="NullBooleanField 已弃用，请使用 TypedChoiceField 或 BooleanField(null=True)",
                fix_hint="TypedChoiceField(choices=[(None,'未知'),(True,'有'),(False,'没有')])",
            )
        )
    return findings


L1_DETECTORS: list[tuple[str, object]] = [
    ("datetime_now", detect_datetime_now),
    ("jsonfield_default", detect_jsonfield_default),
    ("nullbooleanfield", detect_nullbooleanfield),
]
