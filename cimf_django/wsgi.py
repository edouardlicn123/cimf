"""
WSGI config for cimf_django project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cimf_django.settings')

application = get_wsgi_application()

# 初始化 Cron 服务（仅在 WSGI 服务器启动时）
from core.services import init_cron_service
init_cron_service()
