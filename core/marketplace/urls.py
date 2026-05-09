# -*- coding: utf-8 -*-
"""
模块市场 URL 路由
"""

from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.market_index, name='index'),
    path('install/<str:module_id>/', views.market_install, name='install'),
]
