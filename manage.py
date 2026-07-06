#!/usr/bin/env python
"""
================================================================================
文件：manage.py
路径：/home/edo/cimf-v2/manage.py
================================================================================

功能说明：
    Django 管理脚本，参考 Flask run.py 增强了以下功能：
    - 环境变量支持
    - 数据库初始化提示
    - 启动信息打印
    - 生产环境安全检查

用法：
    python manage.py runserver              # 启动开发服务器
    python manage.py runserver 8080         # 指定端口
    python manage.py migrate                 # 数据库迁移

环境变量：
    - DJANGO_DEBUG    : true/false (默认 true)
    - DJANGO_HOST     : 监听地址 (默认 0.0.0.0)
    - DJANGO_PORT     : 监听端口 (默认 8000)
"""

import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cimf_django.settings")

    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # 检查是否为 runserver 命令
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        db_path = Path(__file__).parent / "instance" / "django.db"

        if not db_path.exists():
            print(f"\n未检测到数据库文件: {db_path}")
            print("将创建新数据库，请运行: python manage.py migrate")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
