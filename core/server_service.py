"""服务器启动服务

提供开发服务器启动所需的环境检查、数据库初始化、模块扫描等能力。
"""

import logging
import os
import socket
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class ServerService:
    """服务器启动服务"""

    @classmethod
    def prepare_host_port(cls) -> tuple[str, int]:
        """解析 host/port 环境变量"""
        host = os.environ.get("DJANGO_HOST", "0.0.0.0")
        custom_port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
        port = custom_port or int(os.environ.get("DJANGO_PORT", "8000"))
        return host, port

    @classmethod
    def validate_production(cls) -> None:
        """生产环境安全检查"""
        env = os.environ.get("DJANGO_ENV", "development").lower()

        if env == "production":
            debug_value = os.environ.get("DJANGO_DEBUG", "false").lower() in ("true", "1", "t", "yes", "on")
            if debug_value:
                print("\n" + "=" * 80)
                print("【致命错误】生产环境禁止开启 debug 模式！")
                print("请设置：export DJANGO_ENV=production && export DJANGO_DEBUG=false")
                print("=" * 80 + "\n")
                sys.exit(1)

            try:
                import django  # noqa: PLC0415

                django.setup()
                from django.conf import settings  # noqa: PLC0415

                if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 48:
                    print("\n" + "=" * 80)
                    print("【警告】SECRET_KEY 太弱，建议设置为至少48位随机字符串")
                    print("=" * 80 + "\n")
            except Exception:  # noqa: S110,CIMF_W007 — SECRET_KEY check best-effort
                pass

    @classmethod
    def ensure_migrated(cls) -> None:
        """检查数据库状态，自动执行 migrate"""
        import django  # noqa: PLC0415

        django.setup()
        from django.conf import settings  # noqa: PLC0415

        db_name = settings.DATABASES["default"]["NAME"]
        db_path = Path(db_name)
        if not db_path.is_absolute():
            db_path = Path(settings.BASE_DIR) / db_name

        if not db_path.exists():
            print(f"\n未检测到数据库文件: {db_path}")
            print("将创建新数据库...")
            print("执行 python manage.py migrate ...")
            result = subprocess.run(  # controlled dev command
                ["python", "manage.py", "migrate"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(f"迁移失败: {result.stderr}")
                sys.exit(1)
            print("数据库初始化完成!")
        else:
            print(f"\n数据库路径: {db_path}")

    @classmethod
    def init_modules(cls) -> None:
        """扫描并注册所有 Node 模块"""
        import django  # noqa: PLC0415

        django.setup()
        from core.module.services import ModuleService  # noqa: PLC0415

        print("\n初始化 Node 模块...")
        try:
            modules = ModuleService.scan_modules()
            registered_count = 0
            for m in modules:
                ModuleService.register_module(m)
                registered_count += 1
                print(f"  已注册: {m['name']}")
            print(f"模块注册完成: {registered_count} 个模块")
        except Exception as e:  # noqa: CIMF_W007 — CLI 脚本，print 输出错误
            print(f"模块初始化失败: {e}")

    @classmethod
    def start_cron_background(cls) -> None:
        """在后台线程启动 Cron 服务"""
        def _start():
            import django  # noqa: PLC0415

            django.setup()
            from core.services import init_cron_service  # noqa: PLC0415

            init_cron_service()

        import threading  # noqa: PLC0415

        cron_thread = threading.Thread(target=_start, daemon=True)
        cron_thread.start()

    @classmethod
    def print_banner(cls, host: str, port: int) -> None:
        """打印启动横幅"""
        env = os.environ.get("DJANGO_ENV", "development").lower()
        debug_value = env == "development"

        print("\n" + "=" * 70, flush=True)
        from datetime import UTC, datetime  # noqa: PLC0415

        print(f"CIMF 管理系统启动 ({datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')})", flush=True)
        print(f"Python: {sys.version.split()[0]}", flush=True)
        print(f"环境: {env.upper()}", flush=True)
        print(f"Debug: {debug_value}", flush=True)
        print(f"监听: {host}:{port}", flush=True)

        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            if local_ip != "127.0.0.1":
                print(f"局域网访问: http://{local_ip}:{port}", flush=True)
        except Exception:  # noqa: S110 — IP display best-effort
            pass

        print(f"本地访问: http://localhost:{port}", flush=True)
        print(f"后台管理: http://localhost:{port}/admin/", flush=True)
        print("=" * 70 + "\n", flush=True)

        if env == "production" or not debug_value:
            print("生产环境推荐启动命令：", flush=True)
            print("  gunicorn cimf_django.wsgi:application -w 4 -b 0.0.0.0:8000", flush=True)
            print("-" * 70 + "\n", flush=True)

    @classmethod
    def run_devserver(cls, host: str, port: int) -> None:
        """启动 Django dev server"""
        from django.core.management import execute_from_command_line  # noqa: PLC0415

        sys.argv = ["manage.py", "runserver", f"{host}:{port}", "--noreload"]
        execute_from_command_line(sys.argv)
