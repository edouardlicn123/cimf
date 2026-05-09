# -*- coding: utf-8 -*-
"""
时钟模块 URL 路由
"""

from django.urls import path
from . import views

app_name = 'clock'

urlpatterns = [
    path('api/time/', views.api_time, name='api_time'),
]
