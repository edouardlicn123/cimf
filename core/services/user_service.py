"""
================================================================================
文件：user_service.py
路径：/home/edo/cimf-v2/core/services/user_service.py
================================================================================

功能说明：
    用户管理核心业务逻辑，包括查询列表、新建、编辑、启用/禁用、
    系统管理员保护、统计数据等

    主要功能：
    - 用户 CRUD 操作
    - 密码管理
    - 角色权限处理
    - 系统管理员保护

用法：
    1. 获取用户列表：
        users = UserService.get_user_list(search_term='john', only_active=True)

    2. 创建用户：
        user = UserService.create_user(username='john', nickname='John', password='123456')

    3. 更新用户：
        user = UserService.update_user(user_id=2, nickname='New Name')

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.models.User: 用户模型
    - core.services.permission_service: 权限服务
"""

from django.db.models import Count, Q

from core.constants import UserRole
from core.models import User
from core.services.base_service import BaseService
from core.services.mixins import clean_optional_str, clean_str, update_fields
from core.services.permission_service import PermissionService


class UserService(BaseService):
    """
    用户服务层：封装所有与用户相关的数据库操作和业务规则
    路由层不应直接操作 User 模型
    """

    model_class = User

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User | None:
        """根据 ID 获取用户（排除系统管理员 ID=1）"""
        if user_id == 1:
            return None
        return super().get_by_id(user_id)

    @staticmethod
    def _protect_admin(user_id: int):
        """保护系统管理员账号"""
        if user_id == 1:
            raise PermissionError("系统管理员账号（ID=1）禁止编辑")

    @classmethod
    def _get_user_or_raise(cls, user_id: int) -> User:
        """获取用户，不存在则抛出 ValueError"""
        return cls.get_or_raise(user_id, f"用户不存在 (ID: {user_id})")

    @classmethod
    def get_user_by_username(cls, username: str) -> User | None:
        """通过用户名精确查找用户"""
        return cls.get_first(username=clean_str(username))

    @staticmethod
    def get_user_list(
        search_term: str | None = None, only_active: bool = True, exclude_admin: bool = True, role: str | None = None
    ) -> list[User]:
        """获取用户列表"""
        queryset = User.objects.all()

        if exclude_admin:
            queryset = queryset.exclude(id=1)

        if search_term:
            search = search_term.strip()
            queryset = queryset.filter(Q(username__icontains=search) | Q(nickname__icontains=search))

        if only_active:
            queryset = queryset.filter(is_active=True)

        if role:
            queryset = queryset.filter(role=role)

        return queryset.order_by("-created_at")

    @staticmethod
    def create_user(
        username: str, nickname: str, email: str | None, password: str, role: str = "employee", is_admin: bool = False
    ) -> User:
        """新建用户"""
        username = clean_str(username)
        nickname = clean_str(nickname or username)
        email = clean_str(email) if email else None

        if not password:
            raise ValueError("密码不能为空")

        if len(password) < 10:
            raise ValueError("密码长度至少 10 个字符")

        if User.objects.filter(username=username).exists():
            raise ValueError("用户名已存在")

        if email and User.objects.filter(email=email).exists():
            raise ValueError("邮箱已存在")

        if role == UserRole.MANAGER:
            permissions = ["*"]
            is_admin = True
        else:
            permissions = PermissionService.get_role_permissions_from_db(role)

        user = User.objects.create_user(
            username=username,
            password=password,
            nickname=nickname,
            email=email,
            role=role,
            permissions=permissions,
            is_admin=is_admin,
            is_active=True,
        )

        return user

    @classmethod
    def update_user(
        cls,
        user_id: int,
        username: str | None = None,
        nickname: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role: str | None = None,
        is_admin: bool | None = None,
        is_active: bool | None = None,
    ) -> User:
        """更新用户信息，严格保护 ID=1"""
        cls._protect_admin(user_id)

        user = cls._get_user_or_raise(user_id)

        if username and clean_str(username) != user.username:
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                raise ValueError("用户名已存在")
            user.username = clean_str(username)

        if nickname:
            user.nickname = clean_str(nickname)

        if email is not None:
            if email:
                if User.objects.filter(email=email).exclude(id=user_id).exists():
                    raise ValueError("邮箱已存在")
                user.email = clean_str(email)
            else:
                user.email = None

        if password:
            user.set_password(password)

        if role is not None:
            user.role = role
            if role == UserRole.MANAGER:
                user.permissions = ["*"]
            else:
                user.permissions = PermissionService.get_role_permissions_from_db(role)

        if is_admin is not None:
            user.is_admin = is_admin

        if is_active is not None:
            user.is_active = is_active

        user.save()
        return user

    @classmethod
    def toggle_user_active(cls, user_id: int, active: bool = True) -> User:
        """切换用户启用/禁用状态，保护 ID=1"""
        cls._protect_admin(user_id)

        user = cls._get_user_or_raise(user_id)

        if user.is_active == active:
            return user

        user.is_active = active
        user.save()
        return user

    @staticmethod
    def get_user_stats() -> dict:
        """获取用户统计数据"""
        total = User.objects.filter(is_active=True).count()
        role_counts = User.objects.filter(is_active=True).values("role").annotate(count=Count("id"))
        role_map = {r["role"]: r["count"] for r in role_counts}
        return {
            "total": total,
            "manager": role_map.get(UserRole.MANAGER, 0),
            "leader": role_map.get(UserRole.LEADER, 0),
            "employee": role_map.get(UserRole.EMPLOYEE, 0),
        }

    @classmethod
    def update_profile(cls, user_id: int, nickname: str | None = None, email: str | None = None) -> User:
        """更新用户个人信息（昵称、邮箱）"""
        cls._protect_admin(user_id)
        user = cls._get_user_or_raise(user_id)

        if nickname is not None:
            cleaned = clean_optional_str(nickname)
            user.nickname = cleaned if cleaned else None

        if email is not None:
            if email:
                cleaned_email = clean_str(email)
                if User.objects.filter(email=cleaned_email).exclude(id=user_id).exists():
                    raise ValueError("该邮箱已被其他用户使用")
                user.email = cleaned_email
            else:
                user.email = None

        user.save()
        return user

    @classmethod
    def update_preferences(
        cls,
        user_id: int,
        theme: str | None = None,
        notifications_enabled: bool | None = None,
        preferred_language: str | None = None,
    ) -> User:
        """更新用户偏好设置"""
        user = cls._get_user_or_raise(user_id)
        update_fields(
            user, theme=theme, notifications_enabled=notifications_enabled, preferred_language=preferred_language
        )
        return user

    @classmethod
    def change_password(cls, user_id: int, new_password: str) -> User:
        """修改用户密码"""
        user = cls._get_user_or_raise(user_id)

        user.set_password(new_password)
        user.save()
        return user

    @classmethod
    def get_navigation_cards(cls, user_id: int) -> list:
        """获取用户导航卡片，按position排序"""
        user = cls.get_by_id(user_id)
        if not user:
            return []
        cards = user.navigation_cards or []
        return sorted(cards, key=lambda c: c.get("position", 0) or 99)

    @classmethod
    def save_navigation_cards(cls, user_id: int, cards: list) -> User:
        """保存用户导航卡片"""
        user = cls._get_user_or_raise(user_id)

        if len(cards) > 12:
            raise ValueError("最多只能添加12个导航卡片")

        user.navigation_cards = cards
        user.save(update_fields=["navigation_cards"])
        return user

    @staticmethod
    def assign_position(cards: list) -> int:
        """为新卡片分配第一个空position"""
        used_positions = [c.get("position") for c in cards if c.get("position")]
        for i in range(1, 13):
            if i not in used_positions:
                return i
        return 0  # 已满
