"""
邮件发送服务
"""

from datetime import timedelta

from django.utils import timezone

from core.smtp.models import EmailLog
from core.smtp.services.smtp_service import SmtpService

from .batch_processor import EmailServiceBatchMixin
from .sender import EmailServiceSenderMixin
from .template_sender import EmailServiceTemplateMixin


class EmailService(
    EmailServiceSenderMixin,
    EmailServiceTemplateMixin,
    EmailServiceBatchMixin,
):
    """邮件发送服务"""

    _last_send_time = 0.0
    _next_delay = 0.0

    @classmethod
    def get_send_history(
        cls,
        to_email: str | None = None,
        status: str | None = None,
    ):
        queryset = EmailLog.objects.all()

        if to_email:
            queryset = queryset.filter(to_email__icontains=to_email)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @classmethod
    def cleanup_old_logs(cls) -> int:
        config = SmtpService.get_current_config()
        log_days = config.get("log_days", 30)

        cutoff_date = timezone.now() - timedelta(days=log_days)

        deleted_count, _ = EmailLog.objects.filter(created_at__lt=cutoff_date).delete()

        return deleted_count
