import re
from pathlib import Path

from core.bugscan.detectors.finding import Finding, _source_snippet

HTTP_FALLBACK_RE = re.compile(r"""["']http://(?!(?:localhost|127\.0\.0\.1|0\.0\.0\.0))[^"'\n]*["']""")

MARK_SAFE_FSTRING_RE = re.compile(r"mark_safe\(\s*f['\"]")


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


def detect_http_fallback_url(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in HTTP_FALLBACK_RE.finditer(text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="medium",
                pattern_id="http_fallback_url",
                code=_source_snippet(path, lineno),
                message="使用未加密 HTTP 回退 URL，可能不可达或存在中间人风险",
                fix_hint="升级为 HTTPS 或移除已失效的服务器地址",
            )
        )
    return findings


def detect_mark_safe_fstring(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in MARK_SAFE_FSTRING_RE.finditer(text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="high",
                pattern_id="mark_safe_fstring",
                code=_source_snippet(path, lineno),
                message="mark_safe 内使用了 f-string 插值，请确认所有变量已 html.escape()",
                fix_hint="对每个插值变量调用 html.escape() 后再 mark_safe",
            )
        )
    return findings


L1_DETECTORS: list[tuple[str, object]] = [
    ("datetime_now", detect_datetime_now),
    ("jsonfield_default", detect_jsonfield_default),
    ("nullbooleanfield", detect_nullbooleanfield),
    ("http_fallback_url", detect_http_fallback_url),
    ("mark_safe_fstring", detect_mark_safe_fstring),
]
