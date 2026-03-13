# 文件路径：app/models/system_setting.py
# 功能说明：系统设置模型

from app import db
from datetime import datetime


class SystemSetting(db.Model):
    """
    系统设置表 - 键值对存储（每条配置一行）
    整个系统只有多条记录，每条记录代表一个配置项（key + value）
    通过 SettingsService 统一读写，默认值在服务层处理
    """
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True, comment="主键")

    key = db.Column(
        db.String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="配置键名（唯一，例如 'upload_max_size_mb'）"
    )

    value = db.Column(
        db.Text,
        nullable=False,
        comment="配置值（统一存字符串，服务层负责类型转换）"
    )

    description = db.Column(
        db.String(255),
        nullable=True,
        comment="配置项描述"
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="最后更新时间"
    )

    def __repr__(self):
        return f'<SystemSetting {self.key}: {self.value}>'
