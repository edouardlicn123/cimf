# 文件路径：app/modules/taxonomy/forms.py
# 功能说明：Taxonomy 词汇表表单

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TaxonomyForm(FlaskForm):
    """词汇表表单"""
    name = StringField('名称', validators=[DataRequired(), Length(max=128)], render_kw={"class": "form-control", "placeholder": "请输入词汇表名称"})
    slug = StringField('Slug', validators=[DataRequired(), Length(max=128)], render_kw={"class": "form-control", "placeholder": "URL标识，如 gender"})
    description = TextAreaField('描述', validators=[Optional(), Length(max=512)], render_kw={"class": "form-control", "placeholder": "可选描述"})
    submit = SubmitField('保存', render_kw={"class": "btn btn-primary"})


class TaxonomyItemForm(FlaskForm):
    """词汇项表单"""
    name = StringField('名称', validators=[DataRequired(), Length(max=256)], render_kw={"class": "form-control", "placeholder": "请输入词汇项名称"})
    description = TextAreaField('描述', validators=[Optional(), Length(max=512)], render_kw={"class": "form-control", "placeholder": "可选描述"})
    submit = SubmitField('保存', render_kw={"class": "btn btn-primary"})
