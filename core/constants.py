# -*- coding: utf-8 -*-
"""
================================================================================================================================================
文件：constants.py
路径：/home/edo/cimf-v2/core/constants.py
================================================================================================================================================

功能说明：
    项目全局常量定义，包含版本号、角色、主题、模块类型、语言等。
    
    该文件不导入任何项目内部模块，避免循环导入问题。
    
版本：
    - 2.0: 重构为集中化常量

版本历史：
    - 1.000: 初始版本（仅版本号）
    - 2.000: 2026-05-02 - 集中化常量定义
"""

# ============================================================
# 系统版本
# ============================================================

VERSION_MAJOR = '1'
VERSION_MINOR = 829

def get_version_display():
    return f"v{VERSION_MAJOR}.{VERSION_MINOR:03d}"


# ============================================================
# 用户角色
# ============================================================

class UserRole:
    """用户角色常量"""
    MANAGER = 'manager'
    LEADER = 'leader'
    EMPLOYEE = 'employee'
    
    CHOICES = [
        (MANAGER, '一类用户'),
        (LEADER, '二类用户'),
        (EMPLOYEE, '三类用户'),
    ]
    
    LABELS = {
        MANAGER: '一类用户',
        LEADER: '二类用户',
        EMPLOYEE: '三类用户',
    }
    
    BADGE_CLASSES = {
        MANAGER: 'bg-danger',
        LEADER: 'bg-warning text-dark',
        EMPLOYEE: 'bg-secondary',
    }


# ============================================================
# 用户主题
# ============================================================

class UserTheme:
    """用户主题常量"""
    DEFAULT = 'default'
    GOV = 'gov'
    INDIGO = 'indigo'
    MACARON = 'macaron'
    SAVAWOKU = 'savawoku'
    KAJIMA = 'kajima'
    ODOGU = 'odoru'
    TAIS = 'tais'
    
    CHOICES = [
        (DEFAULT, '默认'),
        (GOV, '浓重红色'),
        (INDIGO, '靛蓝'),
        (MACARON, '马卡龙'),
        (SAVAWOKU, '橙红'),
        (KAJIMA, '绿岛森林'),
        (ODOGU, '踊'),
        (TAIS, '梵紫'),
    ]
    
    LABELS = {
        DEFAULT: '默认',
        GOV: '浓重红色',
        INDIGO: '靛蓝',
        MACARON: '马卡龙',
        SAVAWOKU: '橙红',
        KAJIMA: '绿岛森林',
        ODOGU: '踊',
        TAIS: '梵紫',
    }
    
    DISPLAY_LABELS = LABELS.copy()


# ============================================================
# 模块类型
# ============================================================

class ModuleType:
    """模块类型常量"""
    NODE = 'node'
    SYSTEM = 'system'
    TOOL = 'tool'
    
    CHOICES = [
        (NODE, '节点模块'),
        (SYSTEM, '系统模块'),
        (TOOL, '工具模块'),
    ]


# ============================================================
# 语言
# ============================================================

class Language:
    """语言常量"""
    ZH = 'zh'
    EN = 'en'
    
    CHOICES = [
        (ZH, '中文（简体）'),
        (EN, 'English'),
    ]
