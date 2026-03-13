# 文件路径：app/forms/auth_forms.py
# 更新日期：2026-02-17
# 功能说明：认证相关 WTForms 表单定义，包括登录表单

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=3, max=64, message='用户名长度为 3-64 个字符')
        ],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入用户名',
            'autocomplete': 'username',
            'autofocus': True
        }
    )

    password = PasswordField(
        '密码',
        validators=[DataRequired(message='密码不能为空')],
        render_kw={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入密码',
            'autocomplete': 'current-password'
        }
    )

    remember_me = BooleanField(
        '记住我',
        render_kw={
            'class': 'form-check-input',
            'role': 'switch'
        }
    )

    submit = SubmitField(
        '登录',
        render_kw={
            'class': 'btn btn-primary btn-lg w-100 fw-semibold mt-3'
        }
    )
