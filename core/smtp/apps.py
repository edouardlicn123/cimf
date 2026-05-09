# -*- coding: utf-8 -*-
"""
SMTP 模块应用配置
"""

from django.apps import AppConfig


class SmtpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.smtp'
    verbose_name = 'SMTP邮件服务'
