"""
SMTP 邮件模块视图
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.decorators import admin_required
from core.smtp.forms import SmtpConfigForm
from core.smtp.models import EmailLog
from core.smtp.services import EmailService, SmtpService
from core.utils.pagination import paginate_queryset


@admin_required
@require_http_methods(["GET", "POST"])
def smtp_config(request):
    """SMTP 配置页面"""
    config = SmtpService.get_current_config()
    presets = SmtpService.get_provider_presets()

    if request.method == "POST":
        form = SmtpConfigForm(request.POST)
        if form.is_valid():
            config_data = form.cleaned_data

            if not config_data.get("password"):
                config_data["password"] = config.get("password", "")

            # 保存配置（无论连接测试结果）
            SmtpService.save_config(config_data)

            # 保存后检测服务连接状态
            test_result, test_msg = SmtpService.update_connection_status()
            if test_result:
                messages.success(request, "SMTP 配置已保存，服务连接正常")
            else:
                messages.warning(request, f"配置已保存，但 SMTP 服务连接失败: {test_msg}")

            return redirect("core:smtp_config")
        else:
            messages.error(request, "表单验证失败，请检查填写内容")
    else:
        initial = {
            "provider": config.get("provider", "gmail_tls"),
            "host": config.get("host", ""),
            "port": config.get("port", 587),
            "use_ssl": config.get("use_ssl", False),
            "use_tls": config.get("use_tls", True),
            "username": config.get("username", ""),
            "password": "",
            "from_email": config.get("from_email", ""),
            "from_name": config.get("from_name", "仙芙CIMF"),
            "timeout": config.get("timeout", 30),
            "skip_verify": config.get("skip_verify", False),
            "enabled": config.get("enabled", False),
            "batch_size": config.get("batch_size", 10),
            "rate_limit": config.get("rate_limit", 0),
            "send_interval": config.get("send_interval", 120),
            "log_days": config.get("log_days", 30),
            "failed_notify": config.get("failed_notify", False),
            "notify_email": config.get("notify_email", ""),
            "system_url": config.get("system_url", ""),
            "use_proxy": config.get("use_proxy", False),
            "proxy_host": config.get("proxy_host", ""),
            "proxy_port": config.get("proxy_port", 10808),
        }
        form = SmtpConfigForm(initial=initial)

    recent_logs = EmailLog.objects.all()[:10]

    return render(
        request,
        "smtp/config.html",
        {
            "form": form,
            "config": config,
            "presets": presets,
            "active_section": "smtp",
            "recent_logs": recent_logs,
        },
    )


@admin_required
@require_http_methods(["POST"])
def smtp_test(request):
    """测试 SMTP 连接"""
    config = SmtpService.get_current_config()
    success, message = SmtpService.test_connection(config)

    # 更新数据库中的连接状态（传入已获取的结果，避免重复测试）
    SmtpService.update_connection_status(success=success, message=message)

    if success:
        messages.success(request, message)
    else:
        # 清理可能包含密码的错误信息
        password = config.get("password", "")
        safe_message = message.replace(password, "***") if password else message
        messages.error(request, safe_message)

    return redirect("core:smtp_config")


@admin_required
def smtp_history(request):
    """发送历史页面"""
    status_filter = request.GET.get("status", "all")

    logs_qs = EmailService.get_send_history()
    if status_filter != "all":
        logs_qs = logs_qs.filter(status=status_filter)

    all_qs = EmailService.get_send_history()
    total_count = all_qs.count()
    sent_count = all_qs.filter(status="sent").count()
    failed_count = all_qs.filter(status="failed").count()
    pending_count = all_qs.filter(status__in=["pending", "sending"]).count()

    page_ctx = paginate_queryset(request, logs_qs, per_page=20)

    return render(
        request,
        "smtp/history.html",
        {
            **page_ctx,
            "filter_status": status_filter,
            "total_count": total_count,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "pending_count": pending_count,
            "active_section": "smtp",
        },
    )


@admin_required
@require_http_methods(["POST"])
def smtp_process_queue(request):
    """手动处理待发送邮件队列"""
    sent_count = EmailService.process_pending_emails()
    if sent_count > 0:
        messages.success(request, f"已处理 {sent_count} 封待发送邮件")
    else:
        messages.info(request, "队列中没有待发送的邮件")
    return redirect("core:smtp_config")


@admin_required
@require_http_methods(["POST"])
def smtp_cleanup_logs(request):
    """手动清理邮件日志"""
    deleted_count = EmailService.cleanup_old_logs()
    messages.success(request, f"已清理 {deleted_count} 条过期日志")

    return redirect("core:smtp_config")
