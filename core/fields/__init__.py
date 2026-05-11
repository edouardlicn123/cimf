"""
字段类型模块，统一导出所有 26 种字段类型

版本：
    - 1.0: 从 Flask 迁移

字段类型列表：
    - string: 单行文本
    - string_long: 短文本
    - text: 带格式文本
    - text_long: 长文本
    - text_with_summary: 带摘要文本
    - boolean: 布尔值
    - integer: 整数
    - decimal: 小数
    - float: 浮点数
    - entity_reference: 实体引用
    - file: 文件
    - image: 图片
    - link: 链接
    - email: 邮箱
    - telephone: 电话
    - datetime: 日期时间
    - timestamp: 时间戳
    - geolocation: 地理位置
    - color: 颜色
    - ai_tags: AI 标签
    - identity: 身份证号
    - masked: 脱敏文本
    - biometric: 生物识别
    - address: 地址
    - gis: GIS 地理信息
    - region_select: 省市区联动
"""

from .address import AddressField
from .ai_tags import AITagsField
from .base import BaseField as BaseField
from .biometric import BiometricField
from .boolean import BooleanField
from .color import ColorField
from .datetime import DatetimeField
from .decimal import DecimalField
from .email import EmailField
from .entity_reference import EntityReferenceField
from .file import FileField
from .float import FloatField
from .geolocation import GeolocationField
from .gis import GISField
from .identity import IdentityField
from .image import ImageField
from .integer import IntegerField
from .link import LinkField
from .masked import MaskedField

# 省市县三级联动选择器
from .region_select import RegionSelectField
from .region_select import RegionSelectWidget as RegionSelectWidget
from .string import StringField
from .string_long import StringLongField
from .telephone import TelephoneField
from .text import TextField
from .text_long import TextLongField
from .text_with_summary import TextWithSummaryField
from .timestamp import TimestampField

FIELD_TYPES = {
    'string': StringField,
    'string_long': StringLongField,
    'text': TextField,
    'text_long': TextLongField,
    'text_with_summary': TextWithSummaryField,
    'boolean': BooleanField,
    'integer': IntegerField,
    'decimal': DecimalField,
    'float': FloatField,
    'entity_reference': EntityReferenceField,
    'file': FileField,
    'image': ImageField,
    'link': LinkField,
    'email': EmailField,
    'telephone': TelephoneField,
    'datetime': DatetimeField,
    'timestamp': TimestampField,
    'geolocation': GeolocationField,
    'color': ColorField,
    'ai_tags': AITagsField,
    'identity': IdentityField,
    'masked': MaskedField,
    'biometric': BiometricField,
    'address': AddressField,
    'gis': GISField,
    'region_select': RegionSelectField,
}


def get_field_type(name: str):
    """获取字段类型类"""
    return FIELD_TYPES.get(name, StringField)


def get_all_field_types():
    """获取所有字段类型"""
    return FIELD_TYPES


def get_field_type_info(name: str) -> dict:
    """获取字段类型详细信息"""
    field_class = FIELD_TYPES.get(name, StringField)
    return {
        'name': field_class.name,
        'label': field_class.label,
        'widget': field_class.widget,
        'properties': field_class.properties,
    }


def get_all_field_types_info() -> list:
    """获取所有字段类型详细信息列表"""
    return [get_field_type_info(name) for name in FIELD_TYPES]
