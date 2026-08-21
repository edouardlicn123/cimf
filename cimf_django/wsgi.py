"""
WSGI config for cimf_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cimf_django.settings")

application = get_wsgi_application()

# 启动任务（SMTP 配置同步、模块自动注册）——需在 django.setup() 完成后、Cron 启动前执行
from core.startup import init_startup_tasks  # noqa: E402

init_startup_tasks()

# 初始化 Cron 服务（仅在 WSGI 服务器启动时）
from core.services import init_cron_service  # noqa: E402

init_cron_service()
