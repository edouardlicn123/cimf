# 文件路径：app/forms/settings_forms.py
# 更新日期：2026-02-17
# 功能说明：用户设置相关 WTForms 表单定义，包括个人信息编辑、偏好设置、修改密码三个独立表单，用于 /settings 页面多表单共存处理

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional, ValidationError
from flask_login import current_user
from app.models import User  # 用于邮箱唯一性校验


class ProfileForm(FlaskForm):
    """个人信息编辑表单（昵称、邮箱）"""
    nickname = StringField(
        '显示昵称',
        validators=[
            Optional(),
            Length(max=64, message='昵称长度不能超过 64 个字符')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '用于仪表盘、项目成员列表等的友好显示名称（可留空）',
            'autocomplete': 'nickname'
        }
    )

    email = StringField(
        '邮箱地址',
        validators=[
            Optional(),
            Email(message='请输入有效的邮箱地址')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '用于密码重置、系统通知、找回账号（可留空）',
            'autocomplete': 'email'
        }
    )

    submit_profile = SubmitField(
        '保存个人信息',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 mt-4 fw-semibold'
        }
    )

    def validate_email(self, field):
        """校验邮箱是否已被其他用户占用（排除当前用户自身）"""
        if field.data:
            existing = User.query.filter(
                User.email == field.data.strip(),
                User.id != current_user.id
            ).first()
            if existing:
                raise ValidationError('该邮箱已被其他用户使用，请更换')


class PreferencesForm(FlaskForm):
    """用户偏好设置表单（主题、通知、语言）"""
    theme = SelectField(
        '界面主题',
        coerce=str,
        choices=[
            ('default', '默认'),
            ('gov', '政府风格 - 酒红配色、沉稳'),
            ('indigo', '靛蓝风格 - 专业沉稳、科技感'),
            ('macaron', '马卡龙风格 - 削弱视觉冲击'),
            ('dopamine', '多巴胺风格 - 高饱和、活力快乐'),
            ('teal', '青绿风格 - 清新现代、适合环保医疗主题'),
            ('uniklo', 'uniklo - 干净线条、经典红白'),
        ],
        default='default',
        render_kw={
            'class': 'form-select form-select-lg'
        }
    )

    notifications = BooleanField(
        '开启系统通知（新项目、任务提醒、消息等）',
        default=True,
        render_kw={
            'class': 'form-check-input',
            'role': 'switch',
            'id': 'notificationsSwitch'
        }
    )

    language = SelectField(
        '界面语言',
        choices=[
            ('zh', '中文（简体）'),
            ('en', 'English'),
        ],
        default='zh',
        render_kw={
            'class': 'form-select form-select-lg'
        }
    )

    submit_preferences = SubmitField(
        '保存偏好设置',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 mt-4 fw-semibold'
        }
    )


class ChangePasswordForm(FlaskForm):
    """修改密码表单 - 安全强化版"""
    current_password = PasswordField(
        '当前密码 *',
        validators=[DataRequired(message='请输入当前密码')],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入当前密码以验证身份',
            'autocomplete': 'current-password'
        }
    )

    new_password = PasswordField(
        '新密码 *',
        validators=[
            DataRequired(message='请输入新密码'),
            Length(min=10, message='新密码至少 10 个字符（建议 12+ 字符）')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 12+ 字符，包含大小写、数字、符号',
            'autocomplete': 'new-password'
        }
    )

    confirm_password = PasswordField(
        '确认新密码 *',
        validators=[
            DataRequired(message='请再次输入新密码'),
            EqualTo('new_password', message='两次输入的新密码不一致')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '请再次输入新密码',
            'autocomplete': 'new-password'
        }
    )

    submit_password = SubmitField(
        '修改密码并重新登录',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 mt-4 fw-semibold'
        }
    )

    def validate_current_password(self, field):
        """校验当前密码是否正确"""
        if not current_user.check_password(field.data):
            raise ValidationError('当前密码输入错误，请重试')

    def validate_new_password(self, field):
        """可选：简单密码强度校验（当前仅长度，建议配合前端 JS 增强）"""
        password = field.data
        # 未来可扩展：检查数字、大小写、特殊字符
        # 示例（注释掉，可启用）：
        # if not any(c.isdigit() for c in password):
        #     raise ValidationError('新密码必须包含至少一个数字')
        # if not any(c.isupper() for c in password):
        #     raise ValidationError('新密码必须包含至少一个大写字母')
        # if not any(c.islower() for c in password):
        #     raise ValidationError('新密码必须包含至少一个小写字母')
        # if not any(c in '!@#$%^&*()_+' for c in password):
        #     raise ValidationError('新密码建议包含特殊字符')
        pass
