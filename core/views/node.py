# -*- coding: utf-8 -*-
"""
节点管理视图模块
"""

from django.shortcuts import render
from core.decorators import admin_required


@admin_required
def structure_dashboard(request):
    """内容结构首页"""
    return render(request, 'structure/structure_dashboard.html', {
        'active_section': 'dashboard',
    })
