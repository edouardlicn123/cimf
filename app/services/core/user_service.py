# 文件路径：app/services/user_service.py
# 更新日期：2026-03-10
# 功能说明：用户管理核心业务逻辑，包括查询列表、新建、编辑、启用/禁用、密码处理、系统管理员保护、统计数据等

from flask import current_app
from sqlalchemy import or_
from datetime import datetime
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.core.permission_service import PermissionService, UserRole


class UserService:
    """
    用户服务层：封装所有与用户相关的数据库操作和业务规则
    路由层不应直接操作 User 模型或 db.session
    """

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """根据 ID 获取用户（排除系统管理员 ID=1）"""
        if user_id == 1:
            return None
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """通过用户名精确查找用户"""
        return User.query.filter_by(username=username.strip()).first()

    @staticmethod
    def get_user_list(search_term: str = None, only_active: bool = True) -> list[User]:
        """获取用户列表（排除系统管理员 ID=1）"""
        query = User.query.filter(User.id != 1)

        if search_term:
            search = f"%{search_term.strip()}%"
            query = query.filter(
                or_(
                    User.username.ilike(search),
                    User.nickname.ilike(search)
                )
            )

        if only_active:
            query = query.filter(User.is_active == True)

        return query.order_by(User.created_at.desc()).all()

    @staticmethod
    def create_user(
        username: str,
        nickname: str,
        email: str | None,
        password: str,
        role: str = 'employee',
        is_admin: bool = False
    ) -> User:
        """新建用户"""
        username = username.strip()
        nickname = (nickname or username).strip()
        email = email.strip() if email else None

        if UserService.get_user_by_username(username):
            raise ValueError("用户名已存在")

        if email and User.query.filter_by(email=email).first():
            raise ValueError("邮箱已存在")

        # 处理角色和权限
        if role == UserRole.ADMIN:
            permissions = ['*']
            is_admin = True
        else:
            permissions = PermissionService.get_role_permissions_from_db(role)

        user = User(
            username=username,
            nickname=nickname,
            email=email,
            role=role,
            permissions=permissions,
            is_admin=is_admin,
            is_active=True,
            created_at=datetime.utcnow(),
            last_login_at=None,
            failed_login_attempts=0
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f"新建用户成功: {username} (ID: {user.id}, 角色: {role})")
        return user

    @staticmethod
    def update_user(
        user_id: int,
        username: str | None = None,
        nickname: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role: str | None = None,
        is_admin: bool | None = None,
        is_active: bool | None = None
    ) -> User:
        """更新用户信息，严格保护 ID=1"""
        if user_id == 1:
            raise PermissionError("系统管理员账号（ID=1）禁止编辑")

        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户不存在 (ID: {user_id})")

        if username and username.strip() != user.username:
            if UserService.get_user_by_username(username):
                raise ValueError("用户名已存在")
            user.username = username.strip()

        if nickname:
            user.nickname = nickname.strip()

        if email is not None:
            if email:
                existing = User.query.filter(User.email == email.strip(), User.id != user_id).first()
                if existing:
                    raise ValueError("邮箱已存在")
                user.email = email.strip()
            else:
                user.email = None

        if password:
            user.set_password(password)

        # 角色修改（ID=1 禁止修改）
        if role is not None:
            if user_id == 1:
                raise PermissionError("系统管理员账号（ID=1）禁止修改角色")
            user.role = role
            # 角色为 admin 时自动设置全部权限
            if role == UserRole.ADMIN:
                user.permissions = ['*']
                user.is_admin = True
            else:
                user.permissions = PermissionService.get_role_permissions_from_db(role)
                user.is_admin = False

        if is_admin is not None:
            if user_id == 1:
                raise PermissionError("系统管理员账号（ID=1）禁止修改权限")
            user.is_admin = is_admin

        if is_active is not None:
            if user_id == 1:
                raise PermissionError("系统管理员账号（ID=1）禁止修改状态")
            user.is_active = is_active

        user.updated_at = datetime.utcnow()
        db.session.commit()

        current_app.logger.info(f"用户更新成功: {user.username} (ID: {user.id})")
        return user

    @staticmethod
    def toggle_user_active(user_id: int, active: bool = True) -> User:
        """切换用户启用/禁用状态，保护 ID=1"""
        if user_id == 1:
            raise PermissionError("系统管理员账号（ID=1）禁止启用/禁用")

        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户不存在 (ID: {user_id})")

        if user.is_active == active:
            return user  # 无需变更

        user.is_active = active
        user.updated_at = datetime.utcnow()
        db.session.commit()

        status = "启用" if active else "禁用"
        current_app.logger.info(f"用户状态变更: {user.username} 已{status} (ID: {user.id})")
        return user

    @staticmethod
    def get_user_stats() -> dict:
        """获取用户统计数据"""
        total = User.query.count()
        active = User.query.filter_by(is_active=True).count()
        admins = User.query.filter_by(role=UserRole.ADMIN).count()
        leaders = User.query.filter_by(role=UserRole.LEADER).count()
        employees = User.query.filter_by(role=UserRole.EMPLOYEE).count()
        return {
            'total_users': total,
            'active_users': active,
            'admin_users': admins,
            'leader_users': leaders,
            'employee_users': employees,
            'active_percentage': round((active / total * 100), 1) if total > 0 else 0.0
        }
