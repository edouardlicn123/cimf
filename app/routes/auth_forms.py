from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional  # Optional 备用

class LoginForm(FlaskForm):
    """
    登录表单
    
    用于 /auth/login 路由，支持用户名+密码登录。
    所有字段均使用 Bootstrap 5 兼容的 class。
    """
    
    username = StringField(
        label='用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=3, max=64, message='用户名长度应为 3-64 个字符')
        ],
        render_kw={
            'placeholder': '请输入用户名',
            'autofocus': True,
            'class': 'form-control form-control-lg rounded-3',
            'autocomplete': 'username',  # 优化浏览器自动填充
            'required': True
        }
    )
    
    password = PasswordField(
        label='密码',
        validators=[
            DataRequired(message='请输入密码'),
            # 可选：未来可加 Length(min=8) 等，但登录时通常不强制显示
        ],
        render_kw={
            'placeholder': '请输入密码',
            'class': 'form-control form-control-lg rounded-3',
            'autocomplete': 'current-password',
            'required': True
        }
    )
    
    remember_me = BooleanField(
        label='记住我（7天内免登录）',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'  # Bootstrap 5 switch 风格（可选）
        }
    )
    
    submit = SubmitField(
        label='登录',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 rounded-3 fw-semibold'
        }
    )

    # 可选：未来扩展点（注释保留）
    # captcha = StringField(
    #     label='验证码',
    #     validators=[DataRequired(message='请输入验证码')],
    #     render_kw={'placeholder': '请输入验证码', 'class': 'form-control form-control-lg'}
    # )
