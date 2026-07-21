"""
Django management command: 检查 Jinja2 模板问题
运行: python manage.py check_templates
"""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

BLOCK_RE = re.compile(r"{%\s*block\s+(\w+)")
EXTENDS_RE = re.compile(r"{%\s*extends\s+\"([^\"]+)\"")
FORM_POST_RE = re.compile(r"<form[^>]*method\s*=\s*\"post\"", re.IGNORECASE)
CSRF_RE = re.compile(r"csrf_input|csrf_token|includes/csrf")
# 只在 {{ }} 中检查 FK 访问
VAR_EXPR_RE = re.compile(r"\{\{[^}]*\|?[^}]*\}\}")
# 匹配 {{ obj.field.subfield }} 模式
FK_IN_VAR_RE = re.compile(r"\{\{\s*(\w+)\.(\w+)\.(\w+)")

# 已知安全的二级属性（不是 FK）
SAFE_SECOND_ATTRS = {
    "paginator",
    "errors",
    "id_for_label",
    "style",
    "classList",
    "dataset",
    "target",
    "value",
    "textContent",
}

# 已知安全的三级属性子串（JS 或 form 模式）
SAFE_SUB_PATTERNS = [
    re.compile(r"window\.\w+\.\w+"),
    re.compile(r"this\.\w+\.\w+"),
    re.compile(r"e(?:vent)?\.target\.\w+"),
    re.compile(r"\w+\.style\.\w+"),
    re.compile(r"\w+\.classList\.\w+"),
    re.compile(r"\w+\.dataset\.\w+"),
    re.compile(r"\w+\.paginator\.\w+"),
    re.compile(r"form\.\w+\.value"),
    re.compile(r"form\.\w+\.errors"),
    re.compile(r"form\.\w+\.id_for_label"),
    re.compile(r"form\.\w+\.has_"),
    re.compile(r"request\.\w+\.\w+"),
    re.compile(r"page_obj\.\w+\.\w+"),
]


def _is_safe_fk(line: str) -> bool:
    """判断 FK 访问模式是否是已知安全的（JS/Form 等）"""
    for pat in SAFE_SUB_PATTERNS:
        if pat.search(line):
            return True
    m = FK_IN_VAR_RE.search(line)
    if m:
        second_attr = m.group(2)
        if second_attr in SAFE_SECOND_ATTRS:
            return True
    return False


class Command(BaseCommand):
    help = "检查 Jinja2 模板的常见问题"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="自动修复可修复的问题",
        )

    def handle(self, *_args, **options):
        errors = []
        template_dirs = getattr(settings, "TEMPLATES", [])
        jinja2_dirs = []
        for t in template_dirs:
            if t.get("BACKEND", "").endswith("Jinja2"):
                jinja2_dirs = t.get("DIRS", [])
                break

        if not jinja2_dirs:
            self.stdout.write(self.style.WARNING("未找到 Jinja2 模板目录"))
            return

        all_templates = {}
        for d in jinja2_dirs:
            d_path = Path(d)
            if not d_path.exists():
                continue
            for f in sorted(d_path.rglob("*.html")):
                rel = str(f.relative_to(d_path))
                all_templates[rel] = f

        base_blocks_cache = {}

        for filepath in all_templates.values():
            content = filepath.read_text(encoding="utf-8")
            lines = content.split("\n")

            block_names = set()
            for m in BLOCK_RE.finditer(content):
                block_names.add(m.group(1))

            # --- 检查1: extends 目标存在 ---
            extends_match = EXTENDS_RE.search(content)
            if extends_match:
                base_rel = extends_match.group(1)
                base_found = False
                for d in jinja2_dirs:
                    if (Path(d) / base_rel).exists():
                        base_found = True
                        if base_rel not in base_blocks_cache:
                            base_content = (Path(d) / base_rel).read_text(encoding="utf-8")
                            base_blocks_cache[base_rel] = set(BLOCK_RE.findall(base_content))
                        break
                if not base_found:
                    errors.append((filepath, 1, f"extends 目标 '{base_rel}' 不存在"))

                # --- 检查2: block 名匹配 base ---
                if base_found and block_names:
                    base_blocks = base_blocks_cache.get(base_rel, set())
                    unknown_blocks = block_names - base_blocks
                    errors.extend(
                        (filepath, 2, f"block '{bn}' 在 base 模板 '{base_rel}' 中未定义")
                        for bn in sorted(unknown_blocks)
                    )

            # --- 检查3: POST 表单缺 csrf_input ---
            if FORM_POST_RE.search(content) and not CSRF_RE.search(content):
                errors.append((filepath, 3, "POST 表单缺少 {{ csrf_input }}"))

            # --- 检查4: 外键 None 访问（只在 {{ }} 中检查）---
            for i, line in enumerate(lines):
                if "{{ " not in line:
                    continue
                if _is_safe_fk(line):
                    continue
                m = FK_IN_VAR_RE.search(line)
                if m:
                    obj, attr, sub = m.group(1), m.group(2), m.group(3)
                    # Skip numbers / version strings
                    if attr == sub and obj.isascii() and not obj.isalpha():
                        continue
                    errors.append(
                        (
                            filepath,
                            4,
                            f"第{i + 1}行: {obj}.{attr}.{sub}（考虑用 {obj}.{attr}_id 守卫或确保非 None）",
                        )
                    )

        # --- 输出结果 ---
        if not errors:
            self.stdout.write(self.style.SUCCESS(f"检查了 {len(all_templates)} 个模板，未发现问题"))
            return

        by_level = {1: "extends", 2: "block 名", 3: "csrf_input", 4: "外键访问"}
        ecount = len(errors)

        # 按级别汇总
        level_count = {}
        for _fp, level, _msg in errors:
            level_count[level] = level_count.get(level, 0) + 1

        self.stdout.write(self.style.WARNING(f"检查了 {len(all_templates)} 个模板，发现 {ecount} 个问题:"))
        for level in sorted(level_count):
            tag = by_level.get(level, "其他")
            self.stdout.write(f"  [{tag}] {level_count[level]} 个")

        for filepath, level, msg in errors:
            rel = Path(filepath).name
            tag = by_level.get(level, "其他")
            self.stdout.write(f"  [{tag}] {rel}: {msg}")

        # --- 自动修复 ---
        if options.get("fix"):
            fixed = 0
            for filepath, level, _msg in errors:
                if level != 3:
                    continue
                content = filepath.read_text(encoding="utf-8")
                new_content = re.sub(
                    r"(<form[^>]*>)",
                    r"\1\n                    {{ csrf_input }}",
                    content,
                    count=1,
                )
                if new_content != content:
                    filepath.write_text(new_content, encoding="utf-8")
                    fixed += 1
                    self.stdout.write(f"  修复: {filepath.name} 添加了 csrf_input")
            self.stdout.write(self.style.SUCCESS(f"自动修复了 {fixed} 个模板"))
