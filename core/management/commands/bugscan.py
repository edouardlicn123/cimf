"""Bug 模式扫描命令

扫描 core/、modules/、cimf_django/ 下的 Python 文件，
检测已知 Bug 模式并输出 JSON 报告，供 AI 定点修复。

用法：
    ./venv/bin/python manage.py bugscan
    ./venv/bin/python manage.py bugscan --stdout     # 同时输出到 stdout
"""

import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from core.bugscan.detectors import scan_all
from core.bugscan.ignore import IgnoreParser
from core.bugscan.reporter import build_report, write_report


class Command(BaseCommand):
    help = "Bug 模式扫描 — 检测已知 Bug 模式并输出 JSON 报告"

    def add_arguments(self, parser):
        parser.add_argument("--stdout", action="store_true", help="同时输出 JSON 到 stdout")

    def handle(self, **options):
        start = time.perf_counter()

        ignore_parser = IgnoreParser()
        ignore_path = Path(__file__).parent.parent.parent.parent / ".bugscanignore"
        ignore_parser.load(ignore_path)

        raw_findings = scan_all()
        rules_applied = len(ignore_parser.rules)
        base = Path(__file__).parent.parent.parent.parent

        filtered: list = []
        ignored_count = 0
        for f in raw_findings:
            rel = str(Path(f.file).relative_to(base))
            f.file = rel
            if ignore_parser.is_ignored(rel, f.line, f.pattern_id):
                ignored_count += 1
            else:
                filtered.append(f)

        time_ms = int((time.perf_counter() - start) * 1000)

        report = build_report(filtered, ignored_count, rules_applied, time_ms)
        report["stats"]["ignored_count"] = ignored_count

        filepath = write_report(report)

        result = {
            "report_file": filepath,
            "total_findings": report["summary"]["total"],
            "ignored": ignored_count,
            "execution_time_ms": time_ms,
        }

        if options["stdout"]:
            self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS(f"Bug 扫描完成: {result['total_findings']} 个发现, {result['ignored']} 条已抑制"))
            self.stdout.write(f"报告: {filepath}")
