#!/usr/bin/env python3
"""Django 开发服务器启动入口

用法：
    python run.py              # 启动开发服务器
    python run.py 8080        # 指定端口
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cimf_django.settings")


def main():
    from core.server_service import ServerService  # noqa: PLC0415

    host, port = ServerService.prepare_host_port()
    ServerService.validate_production()
    ServerService.ensure_migrated()
    ServerService.init_modules()
    ServerService.print_banner(host, port)
    ServerService.start_cron_background()
    ServerService.run_devserver(host, port)


if __name__ == "__main__":
    main()
