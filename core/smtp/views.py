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


@admin_required
@require_http_methods(['GET', 'POST'])
def smtp_config(request):
    """SMTP 配置页面"""
    config = SmtpService.get_current_config()
    presets = SmtpService.get_provider_presets()

    if request.method == 'POST':
        form = SmtpConfigForm(request.POST)
        if form.is_valid():
            config_data = form.cleaned_data

            if not config_data.get('password'):
                config_data['password'] = config.get('password', '')

            # 保存配置（无论连接测试结果）
            SmtpService.save_config(config_data)

            # 保存后检测服务连接状态
            test_result, test_msg = SmtpService.update_connection_status()
            if test_result:
                messages.success(request, 'SMTP 配置已保存，服务连接正常')
            else:
                messages.warning(request, f'配置已保存，但 SMTP 服务连接失败: {test_msg}')

            return redirect('core:smtp_config')
        else:
            messages.error(request, '表单验证失败，请检查填写内容')
    else:
        initial = {
            'provider': config.get('provider', 'gmail_tls'),
            'host': config.get('host', ''),
            'port': config.get('port', 587),
            'use_ssl': config.get('use_ssl', False),
            'use_tls': config.get('use_tls', True),
            'username': config.get('username', ''),
            'password': '',
            'from_email': config.get('from_email', ''),
            'from_name': config.get('from_name', '仙芙CIMF'),
            'timeout': config.get('timeout', 30),
            'skip_verify': config.get('skip_verify', False),
            'enabled': config.get('enabled', False),
            'batch_size': config.get('batch_size', 10),
            'rate_limit': config.get('rate_limit', 0),
            'log_days': config.get('log_days', 30),
            'failed_notify': config.get('failed_notify', False),
            'notify_email': config.get('notify_email', ''),
            'system_url': config.get('system_url', ''),
        }
        form = SmtpConfigForm(initial=initial)

    recent_logs = EmailLog.objects.all()[:10]

    return render(request, 'smtp/config.html', {
        'form': form,
        'config': config,
        'presets': presets,
        'active_section': 'smtp',
        'recent_logs': recent_logs,
    })


@admin_required
@require_http_methods(['POST'])
def smtp_test(request):
    """测试 SMTP 连接"""
    config = SmtpService.get_current_config()
    success, message = SmtpService.test_connection(config)

    if success:
        messages.success(request, message)
    else:
        # 清理可能包含密码的错误信息
        password = config.get('password', '')
        safe_message = message.replace(password, '***') if password else message
        messages.error(request, safe_message)

    return redirect('core:smtp_config')


@admin_required
def smtp_history(request):
    """发送历史页面"""
    status_filter = request.GET.get('status', '')
    logs = EmailService.get_send_history(limit=100, status=status_filter)

    return render(request, 'smtp/history.html', {
        'logs': logs,
        'status_filter': status_filter,
        'active_section': 'smtp',
    })


@admin_required
@require_http_methods(['POST'])
def smtp_cleanup_logs(request):
    """手动清理邮件日志"""
    deleted_count = EmailService.cleanup_old_logs()
    messages.success(request, f'已清理 {deleted_count} 条过期日志')

    return redirect('core:smtp_config')
