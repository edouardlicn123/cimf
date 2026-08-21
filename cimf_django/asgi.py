"""
ASGI config for cimf_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cimf_django.settings")

application = get_asgi_application()

# 启动任务（SMTP 配置同步、模块自动注册）——需在 django.setup() 完成后执行
from core.startup import init_startup_tasks  # noqa: E402

init_startup_tasks()
