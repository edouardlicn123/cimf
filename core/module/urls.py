# -*- coding: utf-8 -*-
"""模块管理 URL 路由"""

from django.urls import path
from . import views

app_name = 'module'

urlpatterns = [
    path('', views.modules_manage, name='list'),
    path('scan/', views.module_scan, name='scan'),
    path('create/', views.module_create, name='create'),
    path('create/action/', views.module_create_action, name='create_action'),
    path('install/<str:module_id>/', views.module_install, name='install'),
    path('enable/<str:module_id>/', views.module_enable, name='enable'),
    path('disable/<str:module_id>/', views.module_disable, name='disable'),
]
