"""
ValidatorService - 字段验证服务

提供字段值验证和类型转换辅助函数
"""

import re
from typing import Any


def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, str(email)))


def convert_boolean(value: Any) -> bool:
    """将多种布尔表示转换为 Python Boolean

    支持的输入格式：
    - 是/否
    - True/False
    - true/false
    - 1/0
    - 1.0/0.0
    - yes/no
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in ["是", "true", "1", "1.0", "yes", "y"]
    return bool(value)
