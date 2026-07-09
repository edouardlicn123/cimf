"""
导入导出视图模块
"""

from django.shortcuts import render

from core.constants import Perm
from core.decorators import permission_required


@permission_required(Perm.IMPORTEXPORT_VIEW)
def importexport_dashboard(request):
    """数据导入导出首页"""
    return render(
        request,
        "importexport/importexport_dashboard.html",
    )
