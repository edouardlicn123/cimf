"""
同步模块命令

扫描 modules/ 目录中的 module.py，与 Module 表对比，
自动注册和安装未注册的模块。

用法:
    ./venv/bin/python manage.py syncmodules          # 执行注册安装
    ./venv/bin/python manage.py syncmodules --dry-run  # 仅预览
"""

from django.core.management.base import BaseCommand

from core.module.services import ModuleRegistryService


class Command(BaseCommand):
    help = "扫描并注册未安装的模块"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅预览要注册的模块，不实际执行",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        dry_run = options.get("dry_run", False)

        result = ModuleRegistryService.scan_register_install(
            do_install=not dry_run,
            dry_run=dry_run,
            respect_install_on_init=True,
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("[模拟] 将处理以下模块："))
        else:
            self.stdout.write(self.style.SUCCESS("扫描完成:"))

        self.stdout.write(f"  已注册: {result['registered']}")
        self.stdout.write(f"  已安装: {result['installed']}")
        self.stdout.write(f"  已跳过: {result['skipped']}")

        if result["failed"]:
            self.stdout.write(self.style.ERROR("  失败:"))
            for fail in result["failed"]:
                self.stdout.write(f"    - {fail}")

        if result["skipped_modules"]:
            self.stdout.write(self.style.WARNING("  因 install_on_init=False 跳过的模块:"))
            for name in result["skipped_modules"]:
                self.stdout.write(f"    - {name}")
