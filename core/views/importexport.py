"""
导入导出视图模块
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.services import PermissionService


@login_required
def importexport_dashboard(request):
    """数据导入导出首页"""
    if not PermissionService.has_permission(request.user, "importexport.view"):
        return redirect("core:dashboard")
    return render(
        request,
        "importexport/importexport_dashboard.html",
    )
