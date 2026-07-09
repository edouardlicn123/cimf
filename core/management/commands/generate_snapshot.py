"""
自动扫描 models/services/views，生成 docs/snapshot_完整.md 和 docs/snapshot_快速参考.md

用法: ./venv/bin/python manage.py generate_snapshot
"""

import ast
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "扫描项目代码，自动生成分层代码快照"

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            type=str,
            help="仅更新指定模块快照（如 customer）",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        base_dir = settings.BASE_DIR
        module_filter = options.get("module")

        models_info = self._scan_models(base_dir, module_filter)
        services_info = self._scan_services(base_dir, module_filter)

        if module_filter:
            self._write_module_snapshot(base_dir, module_filter, models_info, services_info)
        else:
            self._write_full_snapshot(base_dir, models_info, services_info)
            self._write_quick_ref(base_dir, models_info, services_info)
            self._write_all_module_snapshots(base_dir)

        self.stdout.write(self.style.SUCCESS("快照生成完成！"))

    def _scan_models(self, base_dir, module_filter=None):
        """扫描所有 models.py，提取模型字段信息"""
        results = {}
        search_dirs = [
            os.path.join(base_dir, "core"),
        ]
        if not module_filter:
            modules_dir = os.path.join(base_dir, "modules")
            if os.path.isdir(modules_dir):
                for name in os.listdir(modules_dir):
                    if os.path.isdir(os.path.join(modules_dir, name)):
                        search_dirs.append(os.path.join(modules_dir, name))

        for search_dir in search_dirs:
            models_path = os.path.join(search_dir, "models.py")
            if not os.path.isfile(models_path):
                continue

            rel_path = os.path.relpath(models_path, base_dir)

            if module_filter and module_filter not in rel_path:
                continue

            models_data = self._parse_models_file(models_path)
            if models_data:
                results[rel_path] = models_data
                self.stdout.write(f"  扫描: {rel_path} ({len(models_data)} 模型)")

        return results

    def _parse_models_file(self, filepath):
        """解析 models.py，提取模型类及字段"""
        with open(filepath) as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return {}

        models = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [self._get_name(b) for b in node.bases]
                if any("Model" in b for b in bases):
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    fields.append(target.id)
                    models[node.name] = {
                        "bases": bases,
                        "fields": fields,
                    }
        return models

    def _scan_services(self, base_dir, module_filter=None):
        """扫描所有 services 目录/文件，提取服务类及方法"""
        results = {}

        # core/services/
        core_services_dir = os.path.join(base_dir, "core", "services")
        if os.path.isdir(core_services_dir):
            for fname in sorted(os.listdir(core_services_dir)):
                if fname.endswith(".py") and not fname.startswith("_"):
                    filepath = os.path.join(core_services_dir, fname)
                    svc = self._parse_service_file(filepath)
                    if svc:
                        rel = os.path.relpath(filepath, base_dir)
                        results[rel] = svc

        # core/node/services/
        node_svc_dir = os.path.join(base_dir, "core", "node", "services")
        if os.path.isdir(node_svc_dir):
            for fname in sorted(os.listdir(node_svc_dir)):
                if fname.endswith(".py") and not fname.startswith("_"):
                    filepath = os.path.join(node_svc_dir, fname)
                    svc = self._parse_service_file(filepath)
                    if svc:
                        rel = os.path.relpath(filepath, base_dir)
                        results[rel] = svc

        # core/module/
        module_svc = os.path.join(base_dir, "core", "module", "services.py")
        if os.path.isfile(module_svc):
            svc = self._parse_service_file(module_svc)
            if svc:
                results["core/module/services.py"] = svc

        # core/smtp/
        smtp_services = os.path.join(base_dir, "core", "smtp", "services.py")
        if os.path.isfile(smtp_services):
            svc = self._parse_service_file(smtp_services)
            if svc:
                results["core/smtp/services.py"] = svc

        # modules/*/services.py
        modules_dir = os.path.join(base_dir, "modules")
        if not module_filter and os.path.isdir(modules_dir):
            for name in sorted(os.listdir(modules_dir)):
                svc_path = os.path.join(modules_dir, name, "services.py")
                if os.path.isfile(svc_path):
                    svc = self._parse_service_file(svc_path)
                    if svc:
                        rel = os.path.relpath(svc_path, base_dir)
                        results[rel] = svc
                        self.stdout.write(f"  扫描: {rel}")

        return results

    def _parse_service_file(self, filepath):
        with open(filepath) as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return {}

        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = []
                        for arg in item.args.args:
                            if arg.arg != "self" and arg.arg != "cls":
                                args.append(arg.arg)
                        methods.append({
                            "name": item.name,
                            "args": args,
                        })
                if methods:
                    classes[node.name] = {
                        "bases": [self._get_name(b) for b in node.bases],
                        "methods": methods,
                    }
        return classes

    def _write_full_snapshot(self, base_dir, models_info, services_info):
        """生成 snapshot_完整.md"""
        output_path = os.path.join(base_dir, "docs", "snapshot_完整.md")
        lines = [
            "# 代码快照\n",
            f"> 自动生成：{self._today()}",
            "> 用途：避免每次 session 全库扫描，减少 token 消耗",
            "> 快速参考（模型/服务索引）见 `docs/snapshot_快速参考.md`\n",
        ]

        # Model sections
        for rel_path, models in sorted(models_info.items()):
            lines.append(f"### {rel_path}\n")
            lines.append("| 模型 | 基类 | 字段 |")
            lines.append("|------|------|------|")
            for name, info in sorted(models.items()):
                bases_str = ", ".join(info["bases"][:2])
                fields_str = ", ".join(info["fields"][:5])
                if len(info["fields"]) > 5:
                    fields_str += f"... (+{len(info['fields'])-5})"
                lines.append(f"| {name} | {bases_str} | {fields_str} |")
            lines.append("")

        # Service sections
        lines.append("## 服务层签名\n")
        for _rel_path, classes in sorted(services_info.items()):
            for class_name, info in sorted(classes.items()):
                bases_str = ", ".join(info["bases"])
                lines.append(f"### {class_name} ({bases_str})")
                lines.append("| 方法 | 参数 |")
                lines.append("|------|------|")
                for m in info["methods"]:
                    args_str = ", ".join(m["args"][:4])
                    if len(m["args"]) > 4:
                        args_str += "..."
                    lines.append(f"| {m['name']} | {args_str} |")
                lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        self.stdout.write(f"  写入: docs/snapshot_完整.md ({len(lines)} 行)")

    def _write_quick_ref(self, base_dir, models_info, services_info):
        """生成 snapshot_快速参考.md"""
        output_path = os.path.join(base_dir, "docs", "snapshot_快速参考.md")
        lines = [
            "# 代码快照 — 快速参考\n",
            f"> 生成日期：{self._today()} | 用途：快速定位模型/服务，减少全库搜索\n",
        ]

        # Model index
        lines.append("## 模型索引\n")
        lines.append("| 模型 | 文件 |")
        lines.append("|------|------|")
        for rel_path, models in sorted(models_info.items()):
            for name in sorted(models.keys()):
                lines.append(f"| {name} | `{rel_path}` |")
        lines.append("")

        # Service index
        lines.append("## 服务类索引\n")
        lines.append("| 服务 | 文件 | 方法数 |")
        lines.append("|------|------|:------:|")
        for rel_path, classes in sorted(services_info.items()):
            for class_name, info in sorted(classes.items()):
                lines.append(f"| {class_name} | `{rel_path}` | {len(info['methods'])} |")
        lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        self.stdout.write(f"  写入: docs/snapshot_快速参考.md ({len(lines)} 行)")

    def _write_all_module_snapshots(self, base_dir):
        """为每个模块生成单独的快照"""
        modules_dir = os.path.join(base_dir, "modules")
        if not os.path.isdir(modules_dir):
            return

        snapshot_dir = os.path.join(base_dir, "docs", "模块快照")
        os.makedirs(snapshot_dir, exist_ok=True)

        for name in sorted(os.listdir(modules_dir)):
            if name.startswith("_") or name.startswith("."):
                continue
            module_path = os.path.join(modules_dir, name)
            if not os.path.isdir(module_path):
                continue
            self._write_single_module_snapshot(base_dir, name)

    def _write_single_module_snapshot(self, base_dir, module_name):
        models_path = os.path.join(base_dir, "modules", module_name, "models.py")
        services_path = os.path.join(base_dir, "modules", module_name, "services.py")

        output_path = os.path.join(base_dir, "docs", "模块快照", f"{module_name}.md")

        lines = [f"# {module_name} 模块快照\n"]

        if os.path.isfile(models_path):
            models = self._parse_models_file(models_path)
            if models:
                lines.append("## 模型\n| 模型 | 字段 |")
                lines.append("|------|------|")
                for name, info in sorted(models.items()):
                    fields_str = ", ".join(info["fields"][:8])
                    if len(info["fields"]) > 8:
                        fields_str += "..."
                    lines.append(f"| {name} | {fields_str} |")
                lines.append("")

        if os.path.isfile(services_path):
            svc = self._parse_service_file(services_path)
            if svc:
                lines.append("## 服务类\n| 方法 | 参数 |")
                lines.append("|------|------|")
                for class_name, info in sorted(svc.items()):
                    for m in info["methods"]:
                        args_str = ", ".join(m["args"][:4])
                        if len(m["args"]) > 4:
                            args_str += "..."
                        lines.append(f"| {class_name}.{m['name']} | {args_str} |")
                lines.append("")

        lines.append("## 文件")
        for fname in ["models.py", "services.py", "views.py", "forms.py", "module.py"]:
            fpath = os.path.join(base_dir, "modules", module_name, fname)
            if os.path.isfile(fpath):
                with open(fpath) as f:
                    count = sum(1 for _ in f)
                lines.append(f"- `modules/{module_name}/{fname}` ({count} 行)")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
            f.write("\n")
        self.stdout.write(f"  写入: docs/模块快照/{module_name}.md")

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return "?"

    def _today(self):
        from datetime import date
        return date.today().isoformat()
