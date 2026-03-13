# Customer Forms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional


class CustomerForm(FlaskForm):
    """客户表单"""
    customer_name = StringField('客户名称', validators=[DataRequired(), Length(max=200)], 
                                render_kw={"class": "form-control", "placeholder": "请输入客户名称"})
    contact_person = StringField('联系人', validators=[Length(max=100)], 
                                render_kw={"class": "form-control", "placeholder": "请输入联系人姓名"})
    phone = StringField('电话', validators=[Length(max=20)], 
                       render_kw={"class": "form-control", "placeholder": "请输入电话号码"})
    email = StringField('邮箱', validators=[Email(), Length(max=100), Optional()], 
                       render_kw={"class": "form-control", "placeholder": "请输入邮箱地址"})
    address = StringField('地址', validators=[Length(max=500)], 
                        render_kw={"class": "form-control", "placeholder": "请输入地址"})
    customer_type = SelectField('客户类型', coerce=int, choices=[], 
                                render_kw={"class": "form-select"})
    notes = TextAreaField('备注', validators=[Length(max=2000)], 
                         render_kw={"class": "form-control", "placeholder": "请输入备注", "rows": 4})
    submit = SubmitField('保存', render_kw={"class": "btn btn-primary"})
