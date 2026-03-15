# 文件路径：app/models/user.py
# 功能说明：用户模型

from flask_login import UserMixin
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    """
    用户表 - 系统核心实体
    用于登录认证、权限控制、项目归属、个人偏好存储等。
    继承 UserMixin 以支持 Flask-Login 的 current_user、is_authenticated、is_active 等功能。
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="用户ID（主键）")

    username = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="登录用户名（唯一，必填）"
    )

    nickname = db.Column(
        db.String(64),
        nullable=True,
        comment="显示昵称（仪表盘、项目成员列表等处优先显示，可中英文）"
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False,
        comment="密码哈希值（使用 pbkdf2:sha256 高迭代次数生成）"
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=True,
        index=True,
        comment="用户邮箱（可选，用于密码重置、通知等）"
    )

    is_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="是否为系统管理员（拥有后台管理权限）"
    )

    role = db.Column(
        db.String(20),
        default='employee',
        nullable=False,
        comment="角色：admin=管理员 / leader=组长 / employee=普通员工"
    )

    permissions = db.Column(
        db.JSON,
        default=list,
        comment="细粒度权限列表，如 ['system.manage', 'user.manage']"
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment="账号是否可用（False 表示被禁用）"
    )

    failed_login_attempts = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment="连续登录失败次数，达到阈值后临时锁定"
    )
    locked_until = db.Column(
        db.DateTime,
        nullable=True,
        comment="账号临时锁定的截止时间（为空表示未锁定）"
    )

    theme = db.Column(
        db.String(20),
        nullable=False,
        default='default',
        comment="个人界面主题：default / dopamine / macaron / teal / uniklo"
    )
    notifications_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        comment="是否开启系统通知（新项目、任务提醒等）"
    )
    preferred_language = db.Column(
        db.String(10),
        nullable=False,
        default='zh',
        comment="首选界面语言：zh / en"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="账号创建时间（UTC）"
    )
    last_login_at = db.Column(
        db.DateTime,
        nullable=True,
        comment="最后一次成功登录时间（UTC）"
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="最后更新时间（UTC）"
    )

    def __repr__(self):
        display_name = self.nickname or self.username
        return f'<User {display_name} (id:{self.id})>'

    def set_password(self, password: str) -> None:
        """设置密码，使用高强度哈希（pbkdf2:sha256 + 600,000 次迭代，2026年推荐）"""
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256:600000'
        )

    def check_password(self, password: str) -> bool:
        """验证密码是否匹配"""
        return check_password_hash(self.password_hash, password)

    def record_failed_attempt(self) -> None:
        """记录登录失败，达到阈值后锁定账号"""
        self.failed_login_attempts += 1

        LOCK_THRESHOLD = 5
        LOCK_MINUTES = 30

        if self.failed_login_attempts >= LOCK_THRESHOLD:
            self.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)

    def reset_failed_attempts(self) -> None:
        """登录成功或手动重置时，清零失败计数并解除锁定"""
        self.failed_login_attempts = 0
        self.locked_until = None

    def is_locked(self) -> bool:
        """判断账号是否处于锁定状态"""
        return self.locked_until is not None and self.locked_until > datetime.utcnow()

    def record_login(self) -> None:
        """记录成功登录时间（调用后需 commit）"""
        self.last_login_at = datetime.utcnow()
