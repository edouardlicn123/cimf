# -*- coding: utf-8 -*-
"""
================================================================================
文件：email_cleanup_task.py
路径：/home/edo/cimf/core/services/tasks/email_cleanup_task.py
================================================================================

功能说明：
    邮件日志清理任务，定时清理过期的邮件发送记录。
    
版本：
    - 1.0: 新增

依赖：
    - CronTask: 任务基类
"""

import logging
from .base import CronTask

logger = logging.getLogger(__name__)


class EmailCleanupTask(CronTask):
    """
    邮件日志清理任务类
    
    说明：
        定时清理超过保留天数的邮件发送记录。
    """

    name = "email_cleanup"
    
    default_interval = 86400  # 24小时

    @property
    def setting_key_enabled(self) -> str:
        return "cron_email_cleanup_enabled"

    @property
    def setting_key_interval(self) -> str:
        return "cron_email_cleanup_interval"

    def execute(self):
        """执行日志清理"""
        from core.smtp.services import EmailService
        
        count = EmailService.cleanup_old_logs()
        if count > 0:
            logger.info(f"邮件日志清理任务完成: 清理 {count} 条记录")
        else:
            logger.debug("邮件日志清理任务完成: 无过期记录")
