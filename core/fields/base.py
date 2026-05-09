# -*- coding: utf-8 -*-
"""
===============================================================================
文件：base.py
路径：/home/edo/cimf-v2/core/fields/base.py
===============================================================================

功能说明：
    字段类型基类，所有自定义字段类型继承此基类
    
    提供通用渲染和验证方法，子类可直接调用减少重复代码。
    
版本：
    - 1.0: 从 Flask 迁移
    - 2.0: 增强通用方法，减少子类代码重复

依赖：
    - 无
"""

import re


class BaseField:
    """字段类型基类"""
    name = None
    label = None
    widget = None
    properties = []
    
    def __init__(self, field_name: str, field_config: dict):
        self.field_name = field_name
        self.field_config = field_config
    
    # ========== 通用渲染方法 ==========
    
    def _render_input(self, input_type='text', **kwargs) -> str:
        """通用输入框渲染
        
        参数：
            input_type: input 类型 (text, password, email, tel, number 等)
            **kwargs: 额外属性 (max_length, placeholder, required, disabled 等)
        """
        value = self.field_config.get('value', '')
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        max_length = self.field_config.get('max_length', '')
        
        attrs = f'class="form-control" '
        if required:
            attrs += 'required '
        if placeholder:
            attrs += f'placeholder="{placeholder}" '
        if max_length:
            attrs += f'maxlength="{max_length}" '
        
        for k, v in kwargs.items():
            attrs += f'{k}="{v}" '
        
        return f'<input type="{input_type}" name="{self.field_name}" value="{value}" {attrs}>'
    
    def _render_textarea(self, rows=3, **kwargs) -> str:
        """通用文本域渲染
        
        参数：
            rows: 行数
            **kwargs: 额外属性
        """
        value = self.field_config.get('value', '')
        required = self.field_config.get('required', False)
        
        attrs = f'class="form-control" rows="{rows}" '
        if required:
            attrs += 'required '
        for k, v in kwargs.items():
            attrs += f'{k}="{v}" '
        
        return f'<textarea name="{self.field_name}" {attrs}>{value}</textarea>'
    
    def _render_select(self, choices: list, **kwargs) -> str:
        """通用下拉选择渲染
        
        参数：
            choices: [(value, label), ...] 选项列表
            **kwargs: 额外属性
        """
        value = self.field_config.get('value', '')
        required = self.field_config.get('required', False)
        
        options = ''.join(
            f'<option value="{c[0]}" {"selected" if str(c[0]) == str(value) else ""}>{c[1]}</option>'
            for c in choices
        )
        
        attrs = 'class="form-control" '
        if required:
            attrs += 'required '
        for k, v in kwargs.items():
            attrs += f'{k}="{v}" '
        
        return f'<select name="{self.field_name}" {attrs}>{options}</select>'
    
    def _render_checkbox(self, label=None) -> str:
        """通用复选框渲染
        
        参数：
            label: 显示标签
        """
        value = self.field_config.get('value', False)
        checked = 'checked' if value else ''
        label_text = label or self.field_config.get('label', self.field_name)
        
        return f'''<div class="form-check">
            <input type="checkbox" name="{self.field_name}" class="form-check-input" id="{self.field_name}" {checked}>
            <label class="form-check-label" for="{self.field_name}">{label_text}</label>
        </div>'''
    
    def _render_radio(self, choices: list, **kwargs) -> str:
        """通用单选框组渲染
        
        参数：
            choices: [(value, label), ...] 选项列表
        """
        value = self.field_config.get('value', '')
        
        options = ''.join(
            f'''<div class="form-check">
                <input type="radio" name="{self.field_name}" class="form-check-input" 
                       id="{self.field_name}_{c[0]}" value="{c[0]}" {"checked" if str(c[0]) == str(value) else ""}>
                <label class="form-check-label" for="{self.field_name}_{c[0]}">{c[1]}</label>
            </div>'''
            for c in choices
        )
        
        return f'<div class="form-check-group">{options}</div>'
    
    # ========== 通用验证方法 ==========
    
    def _validate_required(self, field_name=None) -> list:
        """通用必填验证
        
        参数：
            field_name: 自定义字段名称（可选）
        """
        if self.field_config.get('required') and not self.field_config.get('value'):
            label = field_name or self.field_config.get('label', self.field_name)
            return [f'{label} 为必填项']
        return []
    
    def _validate_length(self, min_length=None, max_length=None) -> list:
        """通用长度验证
        
        参数：
            min_length: 最小长度
            max_length: 最大长度
        """
        value = self.field_config.get('value', '')
        errors = []
        
        if min_length and len(value) < min_length:
            errors.append(f'长度不能少于 {min_length} 个字符')
        if max_length and len(value) > max_length:
            errors.append(f'长度不能超过 {max_length} 个字符')
        
        return errors
    
    def _validate_pattern(self, pattern: str, message: str = '格式不正确') -> list:
        """通用正则验证
        
        参数：
            pattern: 正则表达式
            message: 错误提示信息
        """
        value = self.field_config.get('value', '')
        
        if value and not re.match(pattern, value):
            return [message]
        return []
    
    def _validate_range(self, min_value=None, max_value=None) -> list:
        """通用数值范围验证
        
        参数：
            min_value: 最小值
            max_value: 最大值
        """
        try:
            value = float(self.field_config.get('value', 0))
        except (ValueError, TypeError):
            return []
        
        errors = []
        if min_value is not None and value < min_value:
            errors.append(f'值不能小于 {min_value}')
        if max_value is not None and value > max_value:
            errors.append(f'值不能大于 {max_value}')
        
        return errors
    
    # ========== 原有方法保持兼容 ==========
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        """渲染字段表单控件
        
        参数：
            value: 字段当前值
            mode: 渲染模式 (edit/view)
        """
        raise NotImplementedError
    
    def validate(self, value: dict) -> list:
        """验证字段值
        
        参数：
            value: 待验证的值
            
        返回：
            错误信息列表
        """
        return []
    
    def format(self, value) -> any:
        """格式化字段值用于显示
        
        参数：
            value: 原始值
            
        返回：
            格式化后的值
        """
        return value
    
    def get_widget_config(self) -> dict:
        """获取控件配置
        
        返回：
            控件配置字典
        """
        return {}