# -*- coding: utf-8 -*-
"""
海外客户 URL 路由
"""

from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.node_list, name='list'),
    path('create/', views.node_create, name='create'),
    path('<int:node_id>/', views.node_view, name='view'),
    path('<int:node_id>/edit/', views.node_edit, name='edit'),
    path('<int:node_id>/delete/', views.node_delete, name='delete'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
