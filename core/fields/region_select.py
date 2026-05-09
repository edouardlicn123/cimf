# -*- coding: utf-8 -*-
"""
省市县三级联动选择字段
"""

from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse
import json


class RegionSelectWidget(forms.TextInput):
    """省市县三级联动选择器部件（简化版）"""
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control region-select-field', 'type': 'hidden'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # 解析初始值
        initial_data = {'province': '', 'city': '', 'district': '', 'province_name': '', 'city_name': '', 'district_name': ''}
        if value:
            if isinstance(value, str):
                try:
                    initial_data = json.loads(value)
                except Exception:
                    pass
            elif isinstance(value, dict):
                initial_data = value
        
        # 生成三个下拉框
        province_api = reverse('core:api_regions_provinces')
        city_api = reverse('core:api_regions_cities')
        district_api = reverse('core:api_regions_districts')
        
        html = f'''
        <div class="region-select-widget">
            <div class="row">
                <div class="col-md-4">
                    <select class="form-select region-province" id="region-{name}-province" data-target="region-{name}-city" data-api="{province_api}">
                        <option value="">请选择省份</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <select class="form-select region-city" id="region-{name}-city" data-target="region-{name}-district" data-api="{city_api}" disabled>
                        <option value="">请先选择省份</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <select class="form-select region-district" id="region-{name}-district" data-api="{district_api}" disabled>
                        <option value="">请先选择城市</option>
                    </select>
                </div>
            </div>
            <input type="hidden" name="{name}" id="id_{name}" value='{json.dumps(initial_data, ensure_ascii=False)}'>
        </div>
        '''
        return mark_safe(html)
    
    class Media:
        js = ('/js/region_select.js',)


class RegionSelectField(forms.CharField):
    """省市县三级联动选择字段"""
    
    name = 'region_select'
    label = '省市区选择'
    widget = 'select'
    properties = ['province', 'city', 'district', 'province_name', 'city_name', 'district_name']
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs['widget'] = RegionSelectWidget
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """将输入转换为 Python 值"""
        if not value:
            return {'province': '', 'city': '', 'district': '', 'province_name': '', 'city_name': '', 'district_name': ''}
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return {'province': '', 'city': '', 'district': '', 'province_name': '', 'city_name': '', 'district_name': ''}
        
        return {'province': '', 'city': '', 'district': '', 'province_name': '', 'city_name': '', 'district_name': ''}
    
    def prepare_value(self, value):
        """准备用于渲染的值"""
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return value
    
    def clean(self, value):
        """清理数据"""
        data = self.to_python(value)
        return data
    
    def get_prep_value(self, value):
        """准备用于保存的值"""
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return value
