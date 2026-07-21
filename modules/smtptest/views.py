"""
SMTP测试工具视图
"""

import logging
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.module.models import Module, ToolType
from core.smtp.services.email_service import EmailService
from core.smtp.services.smtp_service import SmtpService

logger = logging.getLogger(__name__)


@login_required
def tool_view(request):
    """SMTP测试工具页面"""
    module_ids = Module.get_active_ids("tool")
    tools = ToolType.objects.filter(slug__in=module_ids, is_active=True)

    if request.method == "POST":
        return _handle_send_email(request, tools)
    return render(
        request,
        "smtptest/tool.html",
        {"tools": tools, "active_section": "smtp", "active_tool": "smtptest"},
    )


@require_POST
def _handle_send_email(request, tools):
    subject = request.POST.get("subject", "").strip().replace("\r", " ").replace("\n", " ")
    body = request.POST.get("body", "").strip()
    to_email = request.POST.get("to_email", "").strip()

    if not subject or not body or not to_email:
        messages.error(request, "请填写所有字段")
        return render(
            request,
            "smtptest/tool.html",
            {
                "tools": tools,
                "active_section": "smtp",
                "active_tool": "smtptest",
                "subject": subject,
                "body": body,
                "to_email": to_email,
            },
        )

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, to_email):
        messages.error(request, "邮箱格式不正确")
        return render(
            request,
            "smtptest/tool.html",
            {
                "tools": tools,
                "active_section": "smtp",
                "active_tool": "smtptest",
                "subject": subject,
                "body": body,
                "to_email": to_email,
            },
        )

    smtp_config = SmtpService.get_current_config()
    if not smtp_config.get("enabled"):
        messages.error(request, "SMTP 服务未启用，请先在 SMTP 配置页面启用并保存配置")
        return render(
            request,
            "smtptest/tool.html",
            {
                "tools": tools,
                "active_section": "smtp",
                "active_tool": "smtptest",
                "subject": subject,
                "body": body,
                "to_email": to_email,
            },
        )

    success_count = 0
    log_ids = []

    for i in range(5):
        try:
            log_id = EmailService.send_email(
                to=to_email,
                subject=f"{subject} ({i + 1}/5)",
                body=body,
                async_send=True,
            )
            if log_id:
                log_ids.append(log_id)
                success_count += 1
        except Exception as e:
            logger.error(f"第{i + 1}封邮件发送失败: {e}")

    return render(
        request,
        "smtptest/tool.html",
        {
            "tools": tools,
            "active_section": "smtp",
            "active_tool": "smtptest",
            "sent_count": success_count,
            "total_count": 5,
            "log_ids": log_ids,
            "subject": subject,
            "body": body,
            "to_email": to_email,
        },
    )
