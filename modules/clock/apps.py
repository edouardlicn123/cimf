# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ClockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.clock'
    label = 'clock'
    verbose_name = '时钟'
