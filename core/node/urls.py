# -*- coding: utf-8 -*-
"""Node 节点系统 URL 路由"""

from django.urls import path
from . import views

app_name = 'node'

urlpatterns = [
    path('dashboard/', views.nodes_index, name='index'),
    path('<slug:node_type_slug>/create/', views.module_dispatch, name='node_create', kwargs={'action': 'create'}),
    path('<slug:node_type_slug>/<int:node_id>/', views.module_dispatch, name='node_view'),
    path('<slug:node_type_slug>/<int:node_id>/edit/', views.module_dispatch, name='node_edit'),
    path('<slug:node_type_slug>/<int:node_id>/delete/', views.module_dispatch, name='node_delete', kwargs={'action': 'delete'}),
    path('<slug:node_type_slug>/', views.module_dispatch, name='module_page'),
    # 模块自定义 URL catch-all（如 nodes/customer/api/stats/）
    path('<slug:node_type_slug>/<path:extra_path>/', views.module_custom_dispatch, name='module_custom'),
]
