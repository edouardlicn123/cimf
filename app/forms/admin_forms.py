# 文件路径：app/forms/admin_forms.py
# 更新日期：2026-03-10
# 功能说明：后台管理相关 WTForms 表单定义，包括用户搜索表单、用户新建/编辑表单、权限编辑表单、系统设置批量编辑表单；所有表单均严格校验唯一性、密码强度、权限保护等规则

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError, NumberRange
from flask_login import current_user
from app.models import User
from app.services import UserRole, PermissionService


class UserSearchForm(FlaskForm):
    """用户搜索表单（用于 /admin/system-users 列表页）"""
    username = StringField(
        '用户名 / 昵称',
        validators=[Optional(), Length(max=64)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '输入用户名或昵称搜索（支持模糊匹配）'
        }
    )
    is_active = BooleanField(
        '仅显示启用用户',
        default=True,
        render_kw={
            'class': 'form-check-input',
            'role': 'switch',
            'aria-label': '仅显示启用用户'
        }
    )
    submit = SubmitField(
        '搜索',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 fw-semibold'
        }
    )


class UserForm(FlaskForm):
    """用户新建/编辑表单（用于 /admin/system-user/edit 和 /create）"""

    def __init__(self, *args, is_edit=False, original_username=None, original_email=None, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_edit = is_edit
        self.original_username = (original_username or '').strip()
        self.original_email = (original_email or '').strip()
        self.user_id = user_id
        self.is_admin_user = (user_id == 1) if user_id else False

        # 编辑模式下密码字段可选，新建模式下必填（通过 validate_password 强制）
        if not is_edit:
            self.password.validators = [DataRequired(message='新建用户必须设置密码'), Length(min=10, message='密码至少 10 个字符')]
        else:
            self.password.validators = [Optional(), Length(min=10, message='密码至少 10 个字符')]

    username = StringField(
        '用户名 *',
        validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=3, max=64, message='用户名长度需为 3-64 个字符')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '用于登录的唯一账号（3-64 字符）',
            'autocomplete': 'username'
        }
    )

    nickname = StringField(
        '显示昵称',
        validators=[Optional(), Length(max=64)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '仪表盘、项目成员列表等处显示的友好名称（可留空）',
            'autocomplete': 'name'
        }
    )

    email = StringField(
        '邮箱地址',
        validators=[Optional(), Email(message='请输入有效的邮箱格式')],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '用于密码重置、系统通知（可留空）',
            'autocomplete': 'email'
        }
    )

    password = PasswordField(
        '密码',
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '编辑时留空则不修改密码；新建时必填',
            'autocomplete': 'new-password'
        }
    )

    confirm_password = PasswordField(
        '确认密码',
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '请再次输入密码以确认',
            'autocomplete': 'new-password'
        }
    )

    role = SelectField(
        '用户角色',
        coerce=str,
        choices=UserRole.CHOICES,
        default=UserRole.EMPLOYEE,
        validators=[DataRequired(message='请选择用户角色')],
        render_kw={
            'class': 'form-select form-select-lg'
        }
    )

    is_admin = BooleanField(
        '设为管理员（拥有后台管理权限）',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch',
            'aria-label': '设为管理员'
        }
    )

    is_active = BooleanField(
        '账号启用',
        default=True,
        render_kw={
            'class': 'form-check-input',
            'role': 'switch',
            'aria-label': '账号是否启用'
        }
    )

    submit = SubmitField(
        '保存用户信息',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 fw-semibold mt-4'
        }
    )

    # ──────────────────────────────────────────────
    # 自定义验证器（唯一性、密码一致性、强度等）
    # ──────────────────────────────────────────────

    def validate_username(self, field):
        """用户名唯一性校验：编辑时若未变更则跳过"""
        cleaned = (field.data or '').strip()
        if self.is_edit and cleaned == self.original_username:
            return

        existing = User.query.filter_by(username=cleaned).first()
        if existing:
            raise ValidationError('该用户名已被占用，请更换其他用户名')

    def validate_email(self, field):
        """邮箱唯一性校验：编辑时若未变更则跳过；为空允许"""
        if not field.data:
            return

        cleaned = field.data.strip()

        if self.is_edit and cleaned == self.original_email:
            return

        existing = User.query.filter_by(email=cleaned).first()
        if existing:
            raise ValidationError('该邮箱已被其他用户使用')

    def validate_password(self, field):
        """密码校验：新建必填 + 一致性 + 强度"""
        if field.data:
            # 一致性检查
            if field.data != self.confirm_password.data:
                raise ValidationError('两次输入的密码不一致')

            # 强度建议（最小10位，可选更严格）
            if len(field.data) < 10:
                raise ValidationError('密码长度至少 10 个字符（建议 12+ 字符）')

        else:
            # 新建用户必须设置密码
            if not self.is_edit:
                raise ValidationError('新建用户必须设置密码')

    def validate_confirm_password(self, field):
        """确认密码辅助校验（仅当密码有值时要求）"""
        if self.password.data and not field.data:
            raise ValidationError('请填写确认密码')


class SystemSettingsForm(FlaskForm):
    """
    系统设置表单 - 用于 /admin/system-settings 页面
    所有字段均从 settings_service 的 DEFAULT_SETTINGS 同步
    """
    system_name = StringField(
        '系统名称',
        validators=[DataRequired(), Length(max=60)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '显示在导航栏和页面标题'
        }
    )

    upload_max_size_mb = IntegerField(
        '单个文件最大上传大小 (MB)',
        validators=[DataRequired(), NumberRange(min=5, max=1024)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 10-100 MB，过大可能影响服务器性能'
        }
    )

    upload_max_files = IntegerField(
        '每个项目允许上传的最大文件数',
        validators=[DataRequired(), NumberRange(min=5, max=500)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 10-50 个，防止滥用存储'
        }
    )

    session_timeout_minutes = IntegerField(
        '会话超时时间 (分钟)',
        validators=[DataRequired(), NumberRange(min=5, max=1440)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '30 分钟 = 0.5 小时，1440 = 1 天'
        }
    )

    enable_audit_log = BooleanField(
        '启用操作审计日志（记录用户修改历史）',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    report_watermark_text = StringField(
        '导出报表水印文字',
        validators=[Optional(), Length(max=60)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '例如：内部管理系统 - 内部使用 - 保密'
        }
    )

    # ========== 网页水印设置 ==========
    enable_web_watermark = BooleanField(
        '启用网页水印（登录用户名前景显示）',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    web_watermark_content = SelectMultipleField(
        '水印显示内容',
        choices=[
            ('username', '用户名'),
            ('system_name', '系统名'),
            ('datetime', '时间'),
            ('custom', '自定义文字')
        ],
        render_kw={
            'class': 'form-select form-select-lg',
            'multiple': 'multiple',
            'data-placeholder': '选择显示内容'
        }
    )

    web_watermark_opacity = FloatField(
        '水印透明度',
        validators=[Optional(), NumberRange(min=0.05, max=0.5)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '0.05-0.5，建议 0.15'
        }
    )

    enable_watermark_console_detection = BooleanField(
        '检测控制台打开并警告',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    enable_watermark_shortcut_block = BooleanField(
        '禁用F12等快捷键',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    enable_export_watermark = BooleanField(
        '导出文件添加水印（CSV/Excel）',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    # ========== Cron 调度任务设置 ==========
    cron_cache_cleanup_enabled = BooleanField(
        '启用缓存清理任务',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    cron_cache_cleanup_interval = IntegerField(
        '缓存清理间隔（秒）',
        validators=[Optional(), NumberRange(min=60, max=86400)],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '10800 = 3小时'
        }
    )

    submit = SubmitField(
        '保存系统设置',
        render_kw={
            'class': 'btn btn-primary btn-lg px-5 mt-3 fw-semibold'
        }
    )

    def validate_upload_max_size_mb(self, field):
        """额外校验：大小不能太极端"""
        if field.data > 512:
            # 可选警告，但不阻断
            pass  # 未来可加 flash 提示


class PermissionForm(FlaskForm):
    """权限编辑表单 - 用于 /admin/permissions 页面"""
    submit = SubmitField(
        '保存权限设置',
        render_kw={
            'class': 'btn btn-primary btn-lg px-5 mt-3 fw-semibold'
        }
    )


class RoleNameForm(FlaskForm):
    """角色名称编辑表单 - 用于 /admin/permissions 页面"""
    role_name_leader = StringField(
        '二类角色名称',
        validators=[
            DataRequired(message='请输入二类角色名称'),
            Length(min=2, max=20, message='角色名称长度应为2-20个字符')
        ],
        render_kw={'class': 'form-control', 'placeholder': '例如：课长'}
    )
    role_name_employee = StringField(
        '三类角色名称',
        validators=[
            DataRequired(message='请输入三类角色名称'),
            Length(min=2, max=20, message='角色名称长度应为2-20个字符')
        ],
        render_kw={'class': 'form-control', 'placeholder': '例如：一般员工'}
    )
    submit_role_name = SubmitField(
        '保存名称',
        render_kw={'class': 'btn btn-outline-primary'}
    )
