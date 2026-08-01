"""系统维护工具命令

用法：
    ./venv/bin/python manage.py maintenance backup             数据库备份
    ./venv/bin/python manage.py maintenance clean_cache        清理缓存
    ./venv/bin/python manage.py maintenance generate_secret_key  生成密钥
    ./venv/bin/python manage.py maintenance show_env           查看环境变量
"""

import os
import secrets
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "系统维护工具（备份、清理缓存、密钥生成等）"

    def add_arguments(self, parser):
        parser.add_argument("subcommand", choices=["backup", "clean_cache", "generate_secret_key", "show_env"])

    def handle(self, **options):
        subcommand = options["subcommand"]
        handlers = {
            "backup": self._backup,
            "clean_cache": self._clean_cache,
            "generate_secret_key": self._generate_secret_key,
            "show_env": self._show_env,
        }
        handlers[subcommand]()

    def _backup(self):
        backup_dir = Path(settings.BASE_DIR) / "storage" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        db_name = settings.DATABASES["default"]["NAME"]
        db_path = Path(db_name)

        if not db_path.is_absolute():
            db_path = Path(settings.BASE_DIR) / db_name

        if not db_path.exists():
            self.stdout.write(self.style.WARNING("数据库文件不存在，跳过备份"))
            return

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"django_{timestamp}.db"
        shutil.copy2(db_path, backup_file)
        self.stdout.write(self.style.SUCCESS(f"数据库已备份到: {backup_file}"))

    def _clean_cache(self):
        base = Path(settings.BASE_DIR)

        for pypath in base.rglob("__pycache__"):
            if pypath.is_dir():
                shutil.rmtree(pypath, ignore_errors=True)
        for pattern in ("*.pyc", "*.pyo"):
            for f in base.rglob(pattern):
                f.unlink(missing_ok=True)

        for d in (".pytest_cache", ".coverage", ".mypy_cache", ".ruff_cache"):
            path = base / d
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

        cache_dir = base / "storage" / "staticfiles" / ".cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)

        self.stdout.write(self.style.SUCCESS("缓存清理完成"))

    def _generate_secret_key(self):
        new_key = secrets.token_urlsafe(50)
        env_path = Path(settings.BASE_DIR) / "config.env"

        if not env_path.exists():
            self.stdout.write(self.style.WARNING("config.env 不存在，请先创建"))
            return

        content = env_path.read_text(encoding="utf-8")
        if "SECRET_KEY=" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("SECRET_KEY="):
                    lines[i] = f"SECRET_KEY={new_key}"
                    break
            env_path.write_text("\n".join(lines), encoding="utf-8")
        else:
            with env_path.open("a", encoding="utf-8") as f:
                f.write(f"\nSECRET_KEY={new_key}\n")

        self.stdout.write(self.style.SUCCESS("SECRET_KEY 已更新到 config.env"))

    def _show_env(self):
        for key in ("DJANGO_ENV", "DJANGO_DEBUG", "DJANGO_HOST", "DJANGO_PORT"):
            val = os.environ.get(key, "未设置")
            self.stdout.write(f"  {key}={val}")
        secret = os.environ.get("DJANGO_SECRET_KEY", "")
        self.stdout.write(f"  SECRET_KEY={'已设置' if secret else '未设置'}")
