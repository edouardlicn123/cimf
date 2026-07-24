"""
邮件发送服务 - 批量处理
"""

import logging
import random
import time
from datetime import timedelta

from django.utils import timezone

from core.services import SettingsService
from core.smtp.models import EmailLog
from core.smtp.services.smtp_service import SmtpService

logger = logging.getLogger(__name__)


class EmailServiceBatchMixin:

    @classmethod
    def process_pending_emails(cls) -> int:
        config = SmtpService.get_current_config()
        batch_size = config.get("batch_size", 10)
        send_interval = config.get("send_interval", 240)
        retry_count = int(SettingsService.get_setting("smtp_retry_count", 3))

        elapsed = time.time() - cls._last_send_time
        if elapsed < cls._next_delay:
            logger.debug(f"发送间隔未到，跳过本次处理（已过{elapsed:.0f}s，还需{cls._next_delay - elapsed:.0f}s）")
            return 0

        pending_logs = EmailLog.objects.filter(
            status="pending",
            retry_count__lt=retry_count,
        ).order_by("created_at")[:batch_size]

        sent_count = 0
        for log in pending_logs:
            try:
                log.status = "sending"
                log.save(update_fields=["status"])

                if not config.get("enabled"):
                    log.status = "failed"
                    log.error_message = "SMTP 服务未启用"
                    log.save(update_fields=["status", "error_message"])
                    continue

                to_list = log.to_email.split(",")
                from_email = log.from_email or config.get("username", "")
                default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"

                success = cls._send_sync(
                    to_list=to_list,
                    subject=log.subject,
                    body=log.text_body,
                    html_body=log.html_body,
                    default_from=default_from,
                )

                if success:
                    log.status = "sent"
                    log.sent_at = timezone.now()
                    log.error_message = ""
                    sent_count += 1
                else:
                    log.status = "failed"
                    log.error_message = "发送失败"
                    log.retry_count += 1
                    log.sent_at = None

                log.save(update_fields=["status", "sent_at", "error_message", "retry_count"])

            except Exception as e:
                logger.error(f"处理待发送邮件失败: log_id={log.id}, error={e}", exc_info=True)
                log.status = "failed"
                password = config.get("password", "")
                error_msg = str(e)
                if password and password in error_msg:
                    error_msg = error_msg.replace(password, "***")
                log.error_message = error_msg
                log.retry_count += 1
                log.save(update_fields=["status", "error_message", "retry_count"])

        if sent_count > 0:
            cls._last_send_time = time.time()
            cls._next_delay = send_interval + random.randint(-15, 15)  # noqa: S311 — not crypto, jitter only
            logger.info(f"发送 {sent_count} 封，下次间隔 {cls._next_delay:.0f}s（设定 {send_interval}s ±15s）")
            cls._check_and_notify_failed()

        return sent_count

    @classmethod
    def _check_and_notify_failed(cls) -> None:
        config = SmtpService.get_current_config()

        if not config.get("failed_notify"):
            return

        notify_email = config.get("notify_email", "")
        if not notify_email:
            return

        retry_count = int(SettingsService.get_setting("smtp_retry_count", 3))

        failed_logs = EmailLog.objects.filter(
            status="failed", retry_count__gte=retry_count, created_at__gte=timezone.now() - timedelta(hours=1)
        )

        if not failed_logs.exists():
            return

        failed_count = failed_logs.count()
        subject = f"CIMF 系统邮件发送失败通知 ({failed_count}封)"
        body = f"""您好，

CIMF 系统检测到最近有 {failed_count} 封邮件发送失败，请检查 SMTP 配置。

此邮件由系统自动发送。

-- CIMF 系统"""

        from_email = config.get("from_email", "") or config.get("username", "")
        default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"
        cls._send_sync(
            to_list=[notify_email],
            subject=subject,
            body=body,
            html_body="",
            default_from=default_from,
        )
