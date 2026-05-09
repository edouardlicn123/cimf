# -*- coding: utf-8 -*-
"""
================================================================================
文件：email_sending_task.py
路径：/home/edo/cimf/core/services/tasks/email_sending_task.py
================================================================================

功能说明：
    邮件发送任务，定时处理待发送邮件队列。
    
版本：
    - 1.0: 新增

依赖：
    - CronTask: 任务基类
"""

import logging
from .base import CronTask

logger = logging.getLogger(__name__)


class EmailSendingTask(CronTask):
    """
    邮件发送任务类
    
    说明：
        定时检查并发送待发送邮件队列中的邮件。
    """

    name = "email_sending"
    
    default_interval = 100  # 默认100秒

    @property
    def setting_key_enabled(self) -> str:
        return "cron_email_sending_enabled"

    @property
    def setting_key_interval(self) -> str:
        return "smtp_send_interval"

    def execute(self):
        """执行邮件发送"""
        from core.smtp.services import EmailService
        
        count = EmailService.process_pending_emails()
        if count > 0:
            logger.info(f"邮件发送任务完成: 发送 {count} 封邮件")
        else:
            logger.debug("邮件发送任务完成: 无待发送邮件")
