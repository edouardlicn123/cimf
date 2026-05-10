# -*- coding: utf-8 -*-
"""
邮件发送服务
"""

import time
import logging
from typing import Union, List
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta

from core.smtp.models import EmailLog
from core.smtp.services.smtp_service import SmtpService
from core.smtp.services.template_service import TemplateService
from core.services import SettingsService

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""

    _last_send_time = 0

    @classmethod
    def send_email(
        cls,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        html_body: str = None,
        from_email: str = None,
        async_send: bool = True,
    ) -> Union[bool, int]:
        """
        发送邮件
        
        参数：
            to: 收件人邮箱，可以是单个邮箱或邮箱列表
            subject: 邮件主题
            body: 邮件正文（纯文本）
            html_body: HTML 正文（可选）
            from_email: 发件人地址（可选，默认使用配置）
            async_send: 是否异步发送（默认 True）
        
        返回：
            同步模式返回 bool，异步模式返回 EmailLog ID
        """
        if isinstance(to, str):
            to_list = [to]
        else:
            to_list = to
        
        config = SmtpService.get_current_config()
        
        if not config.get('enabled'):
            return False
        
        from_email = from_email or config.get('from_email')
        if not from_email:
            from_email = config.get('username', '')
        
        default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"
        
        if async_send:
            log = cls._create_log(
                from_email=from_email,
                to_emails=to_list,
                subject=subject,
                text_body=body,
                html_body=html_body,
            )
            
            cls._send_async(log.id)
            return log.id
        else:
            return cls._send_sync(
                to_list=to_list,
                subject=subject,
                body=body,
                html_body=html_body,
                from_email=from_email,
                default_from=default_from,
            )

    @classmethod
    def send_template_email(
        cls,
        to: Union[str, List[str]],
        template_name: str,
        context: dict,
        async_send: bool = True,
    ) -> Union[bool, int]:
        """
        使用模板发送邮件
        
        参数：
            to: 收件人邮箱
            template_name: 模板名称
            context: 模板上下文变量
            async_send: 是否异步发送
        """
        template = TemplateService.get_template(template_name)
        if not template:
            return False
        
        subject = TemplateService.render_subject(template, context)
        html_body, text_body = TemplateService.render_body(template, context)
        
        return cls.send_email(
            to=to,
            subject=subject,
            body=text_body,
            html_body=html_body,
            async_send=async_send,
        )

    @classmethod
    def get_send_history(
        cls,
        to_email: str = None,
        status: str = None,
        limit: int = 50,
    ) -> List[EmailLog]:
        """获取发送历史"""
        queryset = EmailLog.objects.all()
        
        if to_email:
            queryset = queryset.filter(to_email__icontains=to_email)
        if status:
            queryset = queryset.filter(status=status)
        
        return list(queryset[:limit])

    @classmethod
    def _create_log(
        cls,
        from_email: str,
        to_emails: List[str],
        subject: str,
        text_body: str = '',
        html_body: str = '',
        template_name: str = '',
    ) -> EmailLog:
        """创建邮件日志"""
        return EmailLog.objects.create(
            from_email=from_email,
            to_email=','.join(to_emails),
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            template_name=template_name,
            status='pending',
        )

    @classmethod
    def _send_async(cls, log_id: int) -> None:
        """异步发送 - 实际发送由后台任务执行"""
        EmailLog.objects.filter(id=log_id).update(status='pending')

    @classmethod
    def _send_sync(
        cls,
        to_list: List[str],
        subject: str,
        body: str,
        html_body: str,
        from_email: str,
        default_from: str,
    ) -> bool:
        """同步发送邮件"""
        try:
            if html_body:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=default_from,
                    to=to_list,
                )
                msg.attach_alternative(html_body, 'text/html')
                msg.send()
            else:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=default_from,
                    recipient_list=to_list,
                    fail_silently=False,
                )
            return True
        except Exception as e:
            logger.error(f"邮件发送失败: to={to_list}, subject={subject}, error={e}", exc_info=True)
            return False

    @classmethod
    def process_pending_emails(cls) -> int:
        """处理待发送邮件（由定时任务调用）"""
        config = SmtpService.get_current_config()
        batch_size = config.get('batch_size', 10)
        rate_limit = config.get('rate_limit', 0)
        retry_count = int(SettingsService.get_setting('smtp_retry_count', 3))
        
        pending_logs = EmailLog.objects.filter(
            status='pending',
            retry_count__lt=retry_count,
        ).order_by('created_at')[:batch_size]
        
        sent_count = 0
        for log in pending_logs:
            if rate_limit > 0:
                cls._check_rate_limit(rate_limit)
            
            try:
                log.status = 'sending'
                log.save(update_fields=['status'])
                
                if not config.get('enabled'):
                    log.status = 'failed'
                    log.error_message = 'SMTP 服务未启用'
                    log.save(update_fields=['status', 'error_message'])
                    continue
                
                to_list = log.to_email.split(',')
                from_email = log.from_email or config.get('username', '')
                default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"
                
                success = cls._send_sync(
                    to_list=to_list,
                    subject=log.subject,
                    body=log.text_body,
                    html_body=log.html_body,
                    from_email=from_email,
                    default_from=default_from,
                )
                
                if success:
                    log.status = 'sent'
                    log.sent_at = timezone.now()
                    sent_count += 1
                else:
                    log.status = 'failed'
                    log.error_message = '发送失败'
                    log.retry_count += 1
                
                log.save(update_fields=['status', 'sent_at', 'error_message', 'retry_count'])
                
            except Exception as e:
                log.status = 'failed'
                log.error_message = str(e)
                log.retry_count += 1
                log.save(update_fields=['status', 'error_message', 'retry_count'])
        
        if sent_count > 0:
            cls._check_and_notify_failed()
        
        return sent_count

    @classmethod
    def _check_rate_limit(cls, rate_limit: int) -> None:
        """检查并实施速率限制"""
        if rate_limit <= 0:
            return
        
        min_interval = 60.0 / rate_limit
        elapsed = time.time() - cls._last_send_time
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        cls._last_send_time = time.time()

    @classmethod
    def _check_and_notify_failed(cls) -> None:
        """检查失败邮件并通知"""
        config = SmtpService.get_current_config()
        
        if not config.get('failed_notify'):
            return
        
        notify_email = config.get('notify_email', '')
        if not notify_email:
            return
        
        retry_count = int(SettingsService.get_setting('smtp_retry_count', 3))
        
        failed_logs = EmailLog.objects.filter(
            status='failed',
            retry_count__gte=retry_count,
            created_at__gte=timezone.now() - timedelta(hours=1)
        )
        
        if not failed_logs.exists():
            return
        
        failed_count = failed_logs.count()
        subject = f'CIMF 系统邮件发送失败通知 ({failed_count}封)'
        body = f'''您好，

CIMF 系统检测到最近有 {failed_count} 封邮件发送失败，请检查 SMTP 配置。

此邮件由系统自动发送。

-- CIMF 系统'''
        
        from_email = config.get('from_email', '') or config.get('username', '')
        default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"
        cls._send_sync(
            to_list=[notify_email],
            subject=subject,
            body=body,
            html_body='',
            from_email=from_email,
            default_from=default_from,
        )

    @classmethod
    def cleanup_old_logs(cls) -> int:
        """清理过期的邮件日志"""
        config = SmtpService.get_current_config()
        log_days = config.get('log_days', 30)
        
        cutoff_date = timezone.now() - timedelta(days=log_days)
        
        deleted_count, _ = EmailLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        return deleted_count

    @classmethod
    def send_verification_code(
        cls,
        to: str,
        code: str,
        expire_minutes: int = 5,
        request=None,
        async_send: bool = True,
    ) -> Union[bool, int]:
        """
        发送验证码邮件
        
        参数：
            to: 收件人邮箱
            code: 验证码
            expire_minutes: 有效期（分钟）
            request: Django 请求对象（用于获取系统URL）
            async_send: 是否异步发送
        """
        system_url = SmtpService.get_system_url(request)
        context = {
            'code': code,
            'expire_minutes': expire_minutes,
            'system_url': system_url,
            'year': timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name='verification_code',
            context=context,
            async_send=async_send,
        )

    @classmethod
    def send_password_reset(
        cls,
        to: str,
        reset_link: str,
        expire_hours: int = 24,
        request=None,
        async_send: bool = True,
    ) -> Union[bool, int]:
        """
        发送密码重置邮件
        
        参数：
            to: 收件人邮箱
            reset_link: 重置链接
            expire_hours: 有效期（小时）
            request: Django 请求对象
            async_send: 是否异步发送
        """
        system_url = SmtpService.get_system_url(request)
        context = {
            'reset_link': reset_link,
            'expire_hours': expire_hours,
            'system_url': system_url,
            'year': timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name='password_reset',
            context=context,
            async_send=async_send,
        )

    @classmethod
    def send_notification(
        cls,
        to: Union[str, List[str]],
        title: str,
        message: str,
        action_url: str = '',
        action_text: str = '',
        request=None,
        async_send: bool = True,
    ) -> Union[bool, int]:
        """
        发送通知邮件
        
        参数：
            to: 收件人邮箱
            title: 通知标题
            message: 通知内容
            action_url: 操作链接（可选）
            action_text: 操作按钮文字（可选）
            request: Django 请求对象
            async_send: 是否异步发送
        """
        system_url = SmtpService.get_system_url(request)
        context = {
            'title': title,
            'message': message,
            'action_url': action_url,
            'action_text': action_text,
            'system_url': system_url,
            'year': timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name='notification',
            context=context,
            async_send=async_send,
        )
