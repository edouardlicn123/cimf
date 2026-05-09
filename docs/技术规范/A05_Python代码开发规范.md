# Python 代码开发规范

> 文档版本：1.1  
> 最后更新：2026-05-06 — 修正测试文件位置（tests.py→tests/目录拆分）

---

## 一、概述

### 1.1 目的与范围

本规范旨在确保项目代码的一致性、可读性和可维护性。所有参与 cimf-v2 项目开发的开发人员应遵守本规范。

本规范适用于：
- Django Model 定义
- Service 层业务逻辑
- View 层视图函数
- Form 层表单定义
- 测试代码
- 定时任务

### 1.2 项目架构

项目采用「主应用 + 子应用」模式：

```
cimf_django/                    # Django 项目配置
├── settings.py                # 项目设置
├── urls.py                    # 根路由
└── jinja2.py                  # Jinja2 配置

core/                          # 核心应用
├── models.py                  # 核心模型（User, Taxonomy 等）
├── services/                  # 核心服务（目录）
├── views/                     # 核心视图（目录，按功能拆分）
├── forms/                     # 表单定义
├── fields/                    # 自定义字段
├── importexport/              # 导入导出
├── node/                      # 节点系统（动态模块加载）
│   ├── views.py               # module_dispatch 分发器
│   ├── urls.py                # 节点路由
│   ├── models.py              # NodeType 模型
│   └── services/              # 节点服务（目录）
├── module/                    # 模块管理
│   ├── models.py              # Module, ToolType 模型
│   └── services/              # 模块服务（目录）
├── management/                # 管理命令
└── api_urls.py                # REST API 路由（挂载于 /api/v1/）

modules/                       # 业务模块
├── __init__.py
├── urls.py                    # 动态路由加载
├── customer/                  # 海外客户模块
│   ├── __init__.py
│   ├── models.py              # CustomerFields 模型
│   ├── services.py            # 客户服务
│   ├── views.py               # 视图
│   ├── urls.py                # 路由
│   ├── forms.py               # 表单
│   └── templates/             # 模块模板
│
├── clock/                     # 时钟模块
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
```

### 1.3 与现有文档关系

本规范与项目其他技术文档相互关联：

| 文档 | 关系 |
|------|------|
| **A02_模块技术规范.md** | 本规范提供通用代码规范，该文档提供节点业务模块的具体实现指引 |
| **A04_模板开发规范.md** | 本规范定义后端代码规范，该文档定义 Jinja2 模板语法，前者渲染数据供后者使用 |
| **A03_省市县联动字段技术规范.md** | 该文档中的省市区字段实现应遵循本规范的 Model 定义规范 |

### 1.4 代码风格概述

项目代码风格特点：

| 特性 | 说明 |
|------|------|
| **注释风格** | 使用中文文档字符串，遵循项目标准文件头模板 |
| **方法类型** | Service 层以静态方法为主 |
| **类型注解** | 函数参数和返回值使用类型注解 |
| **空值处理** | `.first()` 查询必须做 null 检查 |
| **权限控制** | 统一使用 `PermissionService` + 专用检查函数 |
| **模板引擎** | Jinja2（与 Django 模板语法有差异，见模板开发规范） |

---

## 二、文件头部注释规范

### 2.1 编码声明

所有 Python 文件必须以编码声明开头：

```python
# -*- coding: utf-8 -*-
```

### 2.2 文档字符串模板

项目使用标准化的文件头注释模板，包含五部分：文件信息、路径、功能说明、版本、依赖。

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：<filename>
路径：<file_path>
================================================================================

功能说明：
    <功能描述>
    
    主要功能：
    - <功能点1>
    - <功能点2>
    - <功能点3>

用法：
    1. <用法示例1>
        <具体代码>
    
    2. <用法示例2>
        <具体代码>

版本：
    - 1.0: <初始版本说明>

依赖：
    - <依赖模块1>
    - <依赖模块2>
"""
```

### 2.3 版本与依赖说明

```python
# 正确示例
版本：
    - 1.0: 初始版本
    - 1.1: 添加用户认证功能
    - 1.2: 优化查询性能

依赖：
    - django.contrib.auth: 用户认证
    - django.db: 数据模型
    - core.node.models: 节点模型
```

```python
# 错误示例
版本：1.0  # 缺少版本说明

依赖：  # 依赖不完整或不准确
```

### 2.4 完整示例

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：customer_service.py
路径：/home/edo/cimf/modules/customer/services.py
================================================================================

功能说明：
    客户管理服务，提供客户的 CRUD 操作
    
    主要功能：
    - 获取客户列表
    - 创建/更新/删除客户
    - 获取客户详情

用法：
    1. 获取客户列表：
        customers = CustomerService.get_list(search='keyword')
    
    2. 创建客户：
        customer = CustomerService.create(user=request.user, data={})

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.models.User: 用户模型
    - modules.customer.models.CustomerFields: 客户字段模型
    - core.node.services.NodeService: 节点服务
"""
```

---

## 三、导入规范

### 3.1 import 分组顺序

导入语句按以下顺序排列，组间用空行分隔：

```python
# 第一组：Python 标准库
import time
import logging
import random
import string
from typing import List, Optional, Dict, Any

# 第二组：第三方库
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse

# 第三组：Django 核心模块
from django.db import models

# 第四组：项目内部模块 - core
from core.models import User, Taxonomy
from core.constants import UserRole, UserTheme, ModuleType, Language
from core.services import PermissionService

# 第五组：项目内部模块 - modules
from modules.customer.models import CustomerFields
from modules.customer.services import CustomerService

# 第六组：相对导入（当前应用内）
from . import utils
from ..services import MyService
```

### 3.2 项目内部导入示例

```python
# core 应用内部导入
from core.models import User, SystemSetting
from core.constants import UserRole, ModuleType
from core.services import PermissionService, AuthService
from core.forms import LoginForm

# modules 应用内部导入
from modules.customer.models import CustomerFields
from modules.customer.services import CustomerService
from modules.customer.forms import CustomerForm

# 跨应用导入
from core.services import TaxonomyService  # modules 应用导入 core 服务
from core.constants import ModuleType  # 所有模块均可使用
```

### 3.3 别名使用规范

```python
# 正确示例：避免循环导入时使用别名
from django.contrib.auth import get_user_model

User = get_user_model()  # 必须在函数内或模块底部调用

# 正确示例：常用模块别名
from django.http import Http404 as HttpNotFound  # 如有需要
from django.db.models import Q as DBQ  # 避免与项目 Q 类冲突（可选）
```

### 3.4 避免循环导入

```python
# 错误示例：循环导入
# model_a.py
from .services import ServiceB  # 可能导致循环导入

# service_a.py
from .models import ModelA  # 可能导致循环导入

# 正确示例：使用字符串引用避免循环导入
# model.py
class MyModel(models.Model):
    # 使用字符串引用，避免导入冲突
    user = models.ForeignKey(
        'core.User',  # 字符串引用
        on_delete=models.CASCADE
    )
```

---

## 四、命名规范

### 4.1 模块命名

| 类型 | 规则 | 示例 |
|------|------|------|
| Python 文件 | 小写字母 + 下划线 | `customer_service.py`, `node_service.py` |
| Django 应用 | 小写字母（推荐） | `core/`, `modules/` |
| 业务模块目录 | 小写字母 + 下划线 | `modules/customer/`, `modules/clock/` |
| 包目录 | 小写字母 + 下划线 | `services/`, `forms/` |

### 4.2 类命名

| 类型 | 规则 | 示例 |
|------|------|------|
| Django Model | 大驼峰，描述业务实体 | `class User:`, `class CustomerFields:` |
| Service | 大驼峰，以 Service 结尾 | `class CustomerService:`, `class AuthService:` |
| Form | 大驼峰，以 Form 结尾 | `class LoginForm:`, `class CustomerForm:` |
| View 函数 | 小写字母 + 下划线 | `def node_list(request):` |
| Test Case | 大驼峰，以 TestCase 结尾 | `class UserServiceTestCase:` |

### 4.3 函数命名

```python
# 正确示例
def get_customer_list():
    """获取客户列表"""
    pass

def check_customer_permission(user, node, permission_type: str):
    """检查客户权限"""
    pass

def get_user_by_id(user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    pass
```

### 4.4 变量与常量命名

```python
# 变量命名 - 小写字母 + 下划线
customer_list = []
user_name = "admin"

# 常量命名 - 全大写 + 下划线
MAX_LOGIN_FAILURES = 5
DEFAULT_PAGE_SIZE = 20

# 私有变量 - 单下划线前缀
class MyClass:
    def __init__(self):
        self._private_var = None  # 约定私有
```

### 4.5 Django 特定命名

#### 4.5.1 related_name 命名

```python
# 正确示例：使用小写复数形式 + 描述性后缀
class User(models.Model):
    # 正确：使用描述性名称
    created_nodes = models.ForeignKey(
        'core.node.Node',
        on_delete=models.CASCADE,
        related_name='created_by_users'  # ✓
    )

# 在 Node 模型中
class Node(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_nodes'  # ✓ 与上面匹配
    )
```

#### 4.5.2 verbose_name 命名

```python
# 正确示例：使用中文 verbose_name
customer_name = models.CharField(max_length=200, verbose_name='客户名称')
created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
is_active = models.BooleanField(default=True, verbose_name='是否启用')
```

#### 4.5.3 db_table 命名

```python
# 正确示例：使用小写 + 下划线
class Meta:
    db_table = 'customer_fields'      # ✓
    db_table = 'node_types'           # ✓

# 错误示例
class Meta:
    db_table = 'CustomerFields'       # ✗ 大写
    db_table = 'customerFields'       # ✗ 驼峰
```

---

## 五、类定义规范

### 5.1 Django Model 规范

#### 5.1.1 Meta 类顺序

```python
class CustomerFields(models.Model):
    """客户字段模型"""
    
    # ===== 字段定义 =====
    node = models.OneToOneField(...)
    customer_name = models.CharField(...)
    
    # ===== Meta 类 =====
    class Meta:
        db_table = 'customer_fields'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_name']),
        ]
    
    # ===== 属性方法 =====
    @property
    def creator(self):
        return self.node.created_by if hasattr(self, 'node') and self.node else None
    
    # ===== 字符串表示 =====
    def __str__(self):
        return self.customer_name
```

#### 5.1.2 __str__ 方法

```python
# 正确示例
def __str__(self):
    return self.customer_name  # 返回有意义的字符串

# 错误示例
def __str__(self):
    return f"Customer {self.id}"  # ✗ 不直观

def __str__(self):
    return ""  # ✗ 空字符串无意义
```

#### 5.1.3 TextChoices 使用

```python
# 正确示例
class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = 'manager', '一类用户'
        LEADER = 'leader', '二类用户'
        EMPLOYEE = 'employee', '三类用户'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name='角色'
    )
```

### 5.2 Service 类规范

```python
# 正确示例
class CustomerService:
    """客户管理服务"""
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[CustomerFields]:
        """获取客户列表
        
        Args:
            search: 搜索关键词
            
        Returns:
            客户列表
        """
        queryset = CustomerFields.objects.all()
        if search:
            queryset = queryset.filter(customer_name__icontains=search)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(customer_id: int) -> Optional[CustomerFields]:
        """根据ID获取客户
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户对象或 None
        """
        return CustomerFields.objects.filter(id=customer_id).first()
```

### 5.3 Form 类规范

```python
# 正确示例
class LoginForm(forms.Form):
    """登录表单"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('用户名不能为空')
        return username.strip()
```

### 5.4 方法顺序规范

```python
class MyModel(models.Model):
    """模型说明"""
    
    # ===== 字段定义 =====
    field_one = models.CharField(...)
    field_two = models.ForeignKey(...)
    
    # ===== Meta 类 =====
    class Meta:
        db_table = 'my_table'
    
    # ===== 外部方法（property） =====
    @property
    def computed_field(self):
        return self.field_one
    
    # ===== 私有方法 =====
    def _internal_method(self):
        pass
    
    # ===== 公开方法 =====
    def get_display_name(self):
        return self.field_one
    
    # ===== 类方法 =====
    @classmethod
    def create_default(cls):
        pass
    
    # ===== 静态方法 =====
    @staticmethod
    def utility_function():
        pass
    
    # ===== 字符串表示 =====
    def __str__(self):
        return self.field_one
```

---

## 六、函数规范

### 6.1 参数设计

```python
# 正确示例：使用可选参数和默认值
def get_customer_list(
    search: Optional[str] = None,
    customer_type_id: Optional[int] = None,
    customer_level_id: Optional[int] = None,
    user: Optional[User] = None
) -> List[CustomerFields]:
    """获取客户列表
    
    参数：
        search: 搜索关键词
        customer_type_id: 客户类型ID
        customer_level_id: 客户等级ID
        user: 当前用户，用于权限过滤
    """
    pass

# 错误示例：参数过多或无类型注解
def get_customer_list(search=None, customer_type_id=None, customer_level_id=None, user=None):
    pass
```

### 6.2 返回值类型注解

```python
# 正确示例：明确的返回值类型
def get_by_id(customer_id: int) -> Optional[CustomerFields]:
    """返回 Optional 表示可能为 None"""
    return CustomerFields.objects.filter(id=customer_id).first()

def get_count() -> int:
    """返回具体类型"""
    return CustomerFields.objects.count()

def get_list() -> List[CustomerFields]:
    """返回列表类型"""
    return list(CustomerFields.objects.all())

def get_dict() -> Dict[str, Any]:
    """返回字典类型"""
    return {'key': 'value'}

# 错误示例：无返回值类型
def get_by_id(customer_id: int):
    return CustomerFields.objects.filter(id=customer_id).first()
```

### 6.3 文档字符串规范

```python
# 正确示例：完整的文档字符串
def create(user, data: Dict[str, Any]) -> CustomerFields:
    """创建客户
    
    参数：
        user: 当前用户（创建人）
        data: 客户数据字典
        
    返回：
        创建的客户对象
        
    异常：
        ValidationError: 数据验证失败
        
    示例：
        >>> user = User.objects.get(id=1)
        >>> data = {'customer_name': '测试客户'}
        >>> customer = CustomerService.create(user, data)
        >>> customer.customer_name
        '测试客户'
    """
    pass

# 简洁示例：简单函数
def get_count() -> int:
    """获取客户总数"""
    return CustomerFields.objects.count()
```

### 6.4 lambda 与匿名函数

```python
# 正确示例：简单 lambda
callback = lambda x: x * 2
sort_key = lambda item: item.created_at

# 错误示例：复杂 lambda（应使用命名函数）
# 避免
callback = lambda x: (x.get('a') or '') + (x.get('b') or '') if x.get('a') or x.get('b') else ''

# 正确：使用命名函数
def build_name(item):
    a = item.get('a', '')
    b = item.get('b', '')
    return a + b if a or b else ''

callback = build_name
```

---

## 七、Django 特定规范

### 7.1 查询规范（.first() 空值检查）

这是项目最重要的规范之一，必须严格遵守。

```python
# 正确示例：安全的查询写法
customer = CustomerFields.objects.filter(id=customer_id).first()
if customer is None:
    return None
# 现在可以安全使用 customer
print(customer.customer_name)

# 或者使用早期返回
def get_customer(customer_id: int) -> Optional[CustomerFields]:
    customer = CustomerFields.objects.filter(id=customer_id).first()
    if not customer:
        return None
    return customer

# 错误示例：未检查 null
customer = CustomerFields.objects.filter(id=customer_id).first()
print(customer.customer_name)  # ✗ 如果 customer 是 None，这里会抛出 AttributeError
```

### 7.2 外键安全访问

```python
# 正确示例：安全访问外键
customer = CustomerFields.objects.filter(id=customer_id).first()
if customer and customer.node:
    creator = customer.node.created_by
    if creator:
        print(creator.username)

# 使用 hasattr 安全访问
customer = CustomerFields.objects.filter(id=customer_id).first()
if customer:
    node = getattr(customer, 'node', None)
    if node:
        creator = getattr(node, 'created_by', None)
        if creator:
            print(creator.username)

# 使用 property 方法（推荐）
class CustomerFields(models.Model):
    @property
    def creator(self):
        """获取创建人"""
        if hasattr(self, 'node') and self.node:
            return self.node.created_by
        return None

# 模板中安全访问（在 Jinja2 中）
{{ customer.creator.username|default('未知') }}
```

### 7.3 权限检查模式

项目使用统一的权限检查模式：

```python
# 1. 在 views.py 中定义权限检查函数
def check_customer_permission(user, node, permission_type: str) -> tuple:
    """检查客户节点操作权限
    
    返回: (has_permission: bool, error_message: str)
    """
    if user.is_admin:
        return True, None
    
    is_creator = node.created_by_id == user.id
    
    if is_creator:
        return True, None
    
    perm_map = {
        'view': 'node.customer.view_others',
        'edit': 'node.customer.edit_others',
        'delete': 'node.customer.delete_others',
    }
    
    perm = perm_map.get(permission_type)
    if perm and PermissionService.has_permission(user, perm):
        return True, None
    
    return False, f'您没有权限{permission_type}别人的客户信息'

# 2. 在视图中使用权限检查
@login_required
def node_view(request, node_type_slug: str, node_id: int):
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404('节点不存在')
    
    if node_type_slug == 'customer':
        has_perm, error_msg = check_customer_permission(request.user, node, 'view')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('node:module_page', node_type_slug=node_type_slug)
    
    # 后续处理...
```

### 7.4 表单验证分层

```python
# Service 层：业务逻辑验证
class CustomerService:
    @staticmethod
    def validate_create_data(data: Dict[str, Any]) -> tuple:
        """验证创建数据
        
        返回: (is_valid: bool, errors: Dict[str, str])
        """
        errors = {}
        
        if not data.get('customer_name'):
            errors['customer_name'] = '客户名称不能为空'
        
        if CustomerFields.objects.filter(customer_name=data.get('customer_name')).exists():
            errors['customer_name'] = '客户名称已存在'
        
        return len(errors) == 0, errors

# Form 层：格式验证
class CustomerForm(forms.Form):
    customer_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=False)
    
    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name')
        return name.strip() if name else ''

# 视图中分层使用
@login_required
def node_create(request, node_type_slug: str):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # 先做业务验证
            is_valid, errors = CustomerService.validate_create_data(form.cleaned_data)
            if not is_valid:
                for field, msg in errors.items():
                    form.add_error(field, msg)
                return render(request, 'edit.html', {'form': form})
            
            # 业务验证通过，创建数据
            CustomerService.create(request.user, form.cleaned_data)
            messages.success(request, '创建成功')
            return redirect('node:module_page', node_type_slug)
    else:
        form = CustomerForm()
    return render(request, 'edit.html', {'form': form})
```

### 7.5 消息与重定向

```python
# 正确示例：消息提示 + 重定向
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def delete_customer(request, customer_id: int):
    customer = CustomerService.get_by_id(customer_id)
    if not customer:
        messages.error(request, '客户不存在')
        return redirect('node:module_page', node_type_slug='customer')
    
    CustomerService.delete(customer_id)
    messages.success(request, '客户已删除')
    return redirect('node:module_page', node_type_slug='customer')

# 错误示例：缺少消息反馈
@login_required
def delete_customer(request, customer_id: int):
    CustomerService.delete(customer_id)
    return redirect('node:module_page', node_type_slug='customer')  # ✗ 用户不知道操作结果
```

---

## 八、API 设计规范

### 8.1 RESTful URL 设计

```python
# 正确示例：RESTful URL 设计（统一挂载于 /api/v1/）
# URL 路由（core/api_urls.py，命名空间 api）
path('regions/provinces/', views.api_regions_provinces, name='api_regions_provinces'),
path('customers/', views.customers_api, name='customers_api'),
path('customers/<int:customer_id>/', views.customer_detail_api, name='customer_detail_api'),
path('field-types/', views.field_types_api, name='field_types_api'),
path('taxonomy-items/', views.taxonomy_items_api, name='taxonomy_items_api'),
```

### 8.2 JSON 响应格式

```python
# 正确示例：统一的 JSON 响应格式
from django.http import JsonResponse

def success_response(data=None, message='success', **kwargs):
    """成功响应"""
    response = {
        'success': True,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    response.update(kwargs)
    return JsonResponse(response)

def error_response(message='error', code=None, **kwargs):
    """错误响应"""
    response = {
        'success': False,
        'message': message,
    }
    if code:
        response['code'] = code
    response.update(kwargs)
    return JsonResponse(response)

# 使用示例
def customers_api(request):
    customers = CustomerService.get_list()
    data = [{'id': c.id, 'name': c.customer_name} for c in customers]
    return success_response(data=data)
```

### 8.3 错误响应格式

```python
# 正确示例：标准错误响应
def customers_api(request):
    if not request.user.is_authenticated:
        return error_response(message='需要登录', code='AUTH_REQUIRED')
    
    # 业务逻辑
    return success_response(data=[])

# 错误示例：不一致的响应格式
def customers_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '需要登录'})  # ✗ 与其他 API 格式不一致
    
    return JsonResponse({'status': 'ok'})  # ✗ 字段名不统一
```

### 8.4 认证与授权

```python
# 正确示例：API 认证检查
@login_required
def customers_api(request):
    """需要登录的 API"""
    customers = CustomerService.get_list()
    data = [{'id': c.id, 'name': c.customer_name} for c in customers]
    return JsonResponse({'success': True, 'data': data})

# 需要特定权限的 API
@login_required
def sensitive_api(request):
    if not PermissionService.has_permission(request.user, 'admin.access'):
        return JsonResponse({
            'success': False,
            'message': '需要管理员权限'
        }, status=403)
    # 业务逻辑
```

### 8.5 项目 API 示例

```python
# 词汇表自动补全 API（core/node/views.py:taxonomy_items_api）
@login_required
def taxonomy_items_api(request):
    """词汇表项 autocomplete API"""
    taxonomy_slug = request.GET.get('taxonomy', '')
    search = request.GET.get('q', '')
    
    if not taxonomy_slug:
        return JsonResponse({'items': []})
    
    taxonomy = TaxonomyService.get_taxonomy_by_slug(taxonomy_slug)
    if not taxonomy:
        return JsonResponse({'items': []})
    
    items = TaxonomyService.get_items(taxonomy.id)
    
    if search:
        items = [item for item in items if search.lower() in item.name.lower()]
    
    return JsonResponse({
        'items': [{'id': item.id, 'name': item.name} for item in items]
    })

# 时间 API（core/views/api/time.py）
@login_required
def api_time_current(request):
    """获取当前时间"""
    from core.services import TimeService
    return JsonResponse({
        'success': True,
        'data': {'time': TimeService.get_current_time()}
    })
```

---

## 九、测试规范

### 9.1 测试文件位置

```
项目根目录/
├── tests/
│   ├── core/
│   │   ├── test_models.py      # 模型测试
│   │   ├── test_views.py       # 视图测试
│   │   ├── test_services.py    # 服务测试
│   │   ├── test_forms.py       # 表单测试
│   │   └── test_api.py         # API测试
│   └── modules/
│       ├── clock/              # 时钟模块测试
│       ├── customer/           # 客户模块测试
│       └── __init__.py
└── templates/                  # 模板（不测试）
```

### 9.2 测试类命名

```python
# 正确示例：使用 TestCase 后缀
class UserServiceTestCase(TestCase):
    """用户服务测试"""
    pass

class CustomerServiceTestCase(TestCase):
    """客户服务测试"""
    pass

class LoginFormTestCase(TestCase):
    """登录表单测试"""
    pass

class PermissionTestCase(TestCase):
    """权限测试"""
    pass
```

### 9.3 setUp 方法规范

```python
# 正确示例：完整的 setUp
class CustomerServiceTestCase(TestCase):
    """客户服务测试"""
    
    def setUp(self):
        # 创建测试用户
        self.admin = User.objects.create_user(
            username='admin',
            password='admin12345678',
            role='manager',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            role='employee'
        )
        
        # 创建测试数据
        self.node_type = NodeType.objects.create(
            name='Customer',
            slug='customer',
            icon='bi-people',
            is_active=True
        )
```

### 9.4 断言方法选择

```python
# 正确示例：使用 Django TestCase 断言
def test_get_customer_by_nonexistent_id(self):
    """测试获取不存在的客户应返回 None"""
    result = CustomerService.get_by_id(99999)
    self.assertIsNone(result)  # 断言为 None

def test_get_customer_stats(self):
    """测试获取用户统计"""
    stats = UserService.get_user_stats()
    self.assertIn('total_users', stats)      # 断言包含键
    self.assertIn('active_users', stats)
    self.assertEqual(stats['total_users'], 0)  # 断言相等

def test_login_success(self):
    """测试成功登录"""
    response = self.client.post('/accounts/login/', {
        'username': 'testuser',
        'password': 'test12345678'
    }, follow=True)
    self.assertEqual(response.status_code, 200)  # 断言状态码
```

### 9.5 Service 测试示例

```python
class CustomerServiceTestCase(TestCase):
    """客户服务测试"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin12345678',
            role='manager',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            role='employee'
        )
    
    def test_get_customer_by_nonexistent_id(self):
        """测试获取不存在的客户应返回 None"""
        result = CustomerService.get_by_id(99999)
        self.assertIsNone(result)
    
    def test_get_customer_by_nonexistent_node_id(self):
        """测试通过不存在的节点 ID 获取客户应返回 None"""
        result = CustomerService.get_by_node_id(99999)
        self.assertIsNone(result)
```

### 9.6 View 测试示例

```python
class NodeViewsTestCase(TestCase):
    """节点视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            role='manager',
            is_admin=True
        )
    
    def test_node_delete_nonexistent_node(self):
        """测试删除不存在的节点应该显示错误消息"""
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/modules/customer/delete/99999/')
        self.assertIn(response.status_code, [302, 404])  # 重定向或404都接受


class APITestCase(TestCase):
    """API 测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )
    
    def test_api_time_current_requires_login(self):
        """测试时间 API 需要登录"""
        response = self.client.get('/api/v1/time/current/')
        self.assertEqual(response.status_code, 302)  # 未登录重定向
    
    def test_api_time_current_authenticated(self):
        """测试登录后可以访问时间 API"""
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/v1/time/current/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('time', response.json())
```

### 9.7 测试覆盖率要求

| 类型 | 建议覆盖率 | 说明 |
|------|------------|------|
| Service 层 | ≥80% | 核心业务逻辑必须测试 |
| View 层 | ≥60% | 关键路径必须测试 |
| Model 层 | ≥50% | 验证方法和计算属性必须测试 |

运行测试命令：
```bash
./venv/bin/python manage.py test
```

---

## 十、数据库迁移规范

### 10.1 makemigrations 注意事项

```bash
# 正确示例：清晰描述迁移
./venv/bin/python manage.py makemigrations customer --name add_customer_fields
# 输出：Migrations for 'customer': modules/customer/migrations/0004_add_customer_fields.py

# 错误示例：无意义的名称
./venv/bin/python manage.py makemigrations customer
# 输出：modules/customer/migrations/0004_auto_20240101_0000.py  # 难以理解
```

### 10.2 字段命名规范

```python
# 正确示例：清晰的字段命名
class CustomerFields(models.Model):
    # 使用有意义的字段名
    customer_name = models.CharField(max_length=200, verbose_name='客户名称')
    customer_code = models.CharField(max_length=50, verbose_name='客户代码')
    
    # 外键使用 _id 后缀的字段名（自动生成）
    country = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        related_name='country_customers'
    )
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
```

### 10.3 外键与索引

```python
# 正确示例：合理的外键和索引
class CustomerFields(models.Model):
    customer_name = models.CharField(
        max_length=200,
        unique=True,  # 唯一约束
        verbose_name='客户名称'
    )
    
    class Meta:
        db_table = 'customer_fields'
        indexes = [
            # 常用查询添加索引
            models.Index(fields=['customer_name']),
            models.Index(fields=['created_at']),
        ]
```

### 10.4 数据迁移脚本

```python
# 在迁移文件中添加数据
from django.db import migrations

def create_default_customer_types(apps, schema_editor):
    Taxonomy = apps.get_model('core', 'Taxonomy')
    # 创建默认客户类型...
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('nodes', '0003_xxx'),
    ]
    
    operations = [
        migrations.RunPython(
            create_default_customer_types,
            reverse_code=migrations.RunPython.noop
        ),
    ]
```

### 10.5 迁移后验证

```bash
# 运行迁移
./venv/bin/python manage.py migrate

# 检查迁移状态
./venv/bin/python manage.py showmigrations

# 运行系统检查
./venv/bin/python manage.py check

# 检查特定应用
./venv/bin/python manage.py check nodes
```

### 10.6 字段空值处理规范

**核心原则**：根据 Django 官方最佳实践，不同类型字段的空值处理方式不同。

#### 字段类型与空值对照表

| 字段类型 | Model 定义 | 空值表示 | 说明 |
|----------|------------|----------|------|
| CharField | `blank=True`（不加 `null=True`） | `''` 空字符串 | 避免 NULL 和空字符串混淆 |
| TextField | `blank=True`（不加 `null=True`） | `''` 空字符串 | 同上 |
| EmailField | `blank=True`（不加 `null=True`） | `''` 空字符串 | 同上 |
| URLField | `blank=True`（不加 `null=True`） | `''` 空字符串 | 同上 |
| ForeignKey | `null=True, blank=True` | `None` | 外键必须使用 NULL |
| OneToOneField | `null=True, blank=True` | `None` | 一对一必须使用 NULL |
| DateField | `null=True, blank=True` | `None` | 日期字段使用 NULL |
| DateTimeField | `null=True, blank=True` | `None` | 时间字段使用 NULL |
| IntegerField | `null=True, blank=True` | `None` | 数值字段使用 NULL |
| JSONField | `null=True, blank=True` | `None` | JSON 字段使用 NULL |

#### Model 定义示例

```python
# 正确示例
class CustomerFields(models.Model):
    # CharField：只用 blank，不用 null
    customer_name = models.CharField(max_length=200, verbose_name='客户名称')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    # ForeignKey：必须用 null=True
    country = models.ForeignKey(
        'core.TaxonomyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='country_customers'
    )
    
    # DateField：必须用 null=True
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')

# 错误示例：CharField 使用 null=True
phone = models.CharField(max_length=20, blank=True, null=True)  # ✗ 不推荐
```

#### View 处理示例

**推荐方式：使用 Django Form**

```python
# 正确示例：使用 Form 处理表单数据
@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # form.cleaned_data 已自动处理空值
            # CharField 空值 → ''，ForeignKey 空值 → None
            CustomerService.create(request.user, form.cleaned_data)
            messages.success(request, '创建成功')
            return redirect('node:module_page', node_type_slug='customer')
    else:
        form = CustomerForm()
    return render(request, 'customer/edit.html', {'form': form})
```

**手动处理时的空值规则**（仅在不使用 Form 时参考）：

```python
# CharField：空值 → 空字符串
'name': request.POST.get('name', '').strip(),
'phone': request.POST.get('phone', '').strip(),

# ForeignKey：空值 → None
'country_id': request.POST.get('country') or None,

# DateField：空值 → None
'birth_date': request.POST.get('birth_date') or None,
```

#### 原因说明

1. **数据库层面**：空字符串 `''` 和 `NULL` 是不同的值
2. **查询复杂性**：同时存在 `''` 和 `NULL` 时，查询需要同时处理两种情况
3. **Django 约定**：Django 官方文档明确建议 CharField 不使用 `null=True`
4. **一致性**：统一使用空字符串可简化业务逻辑

---

## 十一、定时任务规范

### 11.1 任务基类使用

项目使用统一的 `CronTask` 基类：

```python
# 正确示例：继承 CronTask
from core.services.tasks.base import CronTask

class TimeSyncTask(CronTask):
    """时间同步任务"""
    
    @property
    def name(self) -> str:
        return "time_sync"
    
    def is_enabled(self) -> bool:
        return SettingsService.get_setting('cron_time_sync_enabled', 'true') == 'true'
    
    def get_interval(self) -> int:
        interval = SettingsService.get_setting('cron_time_sync_interval', '3600')
        return int(interval)
    
    def execute(self):
        """执行任务"""
        from core.services import TimeService
        TimeService.sync_time()
        return "时间同步完成"
```

### 11.2 任务注册与配置

```python
# 在 core/services/cron_service.py 中注册
def init_cron_service():
    """初始化定时任务服务"""
    global _cron_initialized
    if _cron_initialized:
        return
    
    cron = get_cron_service()
    
    # 注册任务
    cron.register(TimeSyncTask())
    cron.register(CacheCleanupTask())
    
    cron.set_app_ready(True)
    cron.start()
```

### 11.3 任务实现示例

```python
# 完整示例：缓存清理任务
class CacheCleanupTask(CronTask):
    """缓存清理任务"""
    
    @property
    def name(self) -> str:
        return "cache_cleanup"
    
    def is_enabled(self) -> bool:
        return SettingsService.get_setting('cron_cache_cleanup_enabled', 'true') == 'true'
    
    def get_interval(self) -> int:
        interval = SettingsService.get_setting('cron_cache_cleanup_interval', '10800')
        return int(interval)
    
    def execute(self):
        """清理过期缓存"""
        from django.core.cache import cache
        cache.clear()
        return "缓存清理完成"
    
    def get_settings_key(self) -> str:
        return "cron_cache_cleanup_enabled"
    
    def get_interval_key(self) -> str:
        return "cron_cache_cleanup_interval"
```

### 11.4 后台线程安全

```python
# 正确示例：线程安全的任务实现
class CronTask:
    """任务基类"""
    
    def execute(self):
        """任务执行逻辑，子类必须实现"""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """任务名称"""
        raise NotImplementedError
    
    def is_enabled(self) -> bool:
        """检查任务是否启用"""
        return True
    
    def get_interval(self) -> int:
        """获取执行间隔（秒）"""
        return 3600
```

### 11.5 任务监控与日志

```python
# 正确示例：任务中的日志记录
import logging

logger = logging.getLogger(__name__)

class TimeSyncTask(CronTask):
    """时间同步任务"""
    
    @property
    def name(self) -> str:
        return "time_sync"
    
    def execute(self):
        try:
            logger.info("开始同步时间...")
            # 业务逻辑
            logger.info("时间同步完成")
            return "完成"
        except Exception as e:
            logger.error(f"时间同步失败: {e}")
            return f"失败: {e}"
```

---

## 附录A 代码模板

### A.1 Model 模板

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：<model_name>.py
路径：<file_path>
================================================================================

功能说明：
    <功能描述>

版本：
    - 1.0: <初始版本>

依赖：
    - <依赖模块>
"""

from django.db import models
from django.conf import settings


class MyModel(models.Model):
    """<模型说明>"""
    
    # ===== 字段定义 =====
    name = models.CharField(max_length=100, verbose_name='名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='创建人'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # ===== Meta 类 =====
    class Meta:
        db_table = '<table_name>'
        verbose_name = '<单数名称>'
        verbose_name_plural = '<复数名称>'
        ordering = ['-created_at']
    
    # ===== 属性方法 =====
    @property
    def creator(self):
        return self.created_by
    
    # ===== 字符串表示 =====
    def __str__(self):
        return self.name
```

### A.2 Service 模板

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：<service_name>.py
路径：<file_path>
================================================================================

功能说明：
    <功能描述>

版本：
    - 1.0: <初始版本>

依赖：
    - <依赖模块>
"""

from typing import List, Optional, Dict, Any
from core.constants import ModuleType
from core.node.models import Node
from modules.customer.models import CustomerFields
from core.node.services import NodeService

User = get_user_model()


class MyService:
    """<服务说明>"""
    
    @staticmethod
    def get_list(search: Optional[str] = None) -> List[MyFields]:
        """获取列表
        
        参数：
            search: 搜索关键词
            
        返回：
            数据列表
        """
        queryset = MyFields.objects.all()
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_by_id(id: int) -> Optional[MyFields]:
        """根据ID获取
        
        参数：
            id: 数据ID
            
        返回：
            数据对象或 None
        """
        return MyFields.objects.filter(id=id).first()
    
    @staticmethod
    def create(user, data: Dict[str, Any]) -> MyFields:
        """创建
        
        参数：
            user: 当前用户
            data: 数据字典
            
        返回：
            创建的对象
        """
        return MyFields.objects.create(**data)
    
    @staticmethod
    def update(id: int, user, data: Dict[str, Any]) -> Optional[MyFields]:
        """更新
        
        参数：
            id: 数据ID
            user: 当前用户
            data: 数据字典
            
        返回：
            更新后的对象或 None
        """
        obj = MyFields.objects.filter(id=id).first()
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        obj.save()
        return obj
    
    @staticmethod
    def delete(id: int) -> bool:
        """删除
        
        参数：
            id: 数据ID
            
        返回：
            是否删除成功
        """
        obj = MyFields.objects.filter(id=id).first()
        if obj:
            obj.delete()
            return True
        return False
```

### A.3 View 模板

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：views.py
路径：<file_path>
================================================================================

功能说明：
    <功能描述>

版本：
    - 1.0: <初始版本>

依赖：
    - <依赖模块>
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from core.node.models import NodeType
from core.node.services import NodeTypeService
from core.services import PermissionService
from core.constants import ModuleType


@login_required
def my_list(request, node_type_slug: str):
    """列表页"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    search = request.GET.get('search', '')
    items = MyService.get_list(search if search else None)
    
    return render(request, 'modules/customer/edit.html', {
        'node_type': node_type,
        'items': items,
        'search': search,
    })


@login_required
def my_create(request, node_type_slug: str):
    """创建页"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        raise Http404('节点类型不存在')
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
        }
        
        try:
            MyService.create(request.user, data)
            messages.success(request, '创建成功')
            return redirect('modules:my_list', node_type_slug=node_type_slug)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'modules/customer/edit.html', {
        'node_type': node_type,
        'item': None,
    })


@login_required
def my_edit(request, node_type_slug: str, item_id: int):
    """编辑页"""
    item = MyService.get_by_id(item_id)
    if not item:
        raise Http404('数据不存在')
    
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name', '').strip(),
        }
        
        try:
            MyService.update(item_id, request.user, data)
            messages.success(request, '更新成功')
            return redirect('modules:my_view', node_type_slug=node_type_slug, item_id=item_id)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'modules/customer/edit.html', {
        'node_type': node_type,
        'item': item,
    })


@login_required
def my_delete(request, node_type_slug: str, item_id: int):
    """删除"""
    item = MyService.get_by_id(item_id)
    if item:
        MyService.delete(item_id)
        messages.success(request, '已删除')
    
    return redirect('modules:my_list', node_type_slug=node_type_slug)
```

### A.4 Form 模板

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：forms.py
路径：<file_path>
================================================================================

功能说明：
    <功能描述>

版本：
    - 1.0: <初始版本>

依赖：
    - <依赖模块>
"""

from django import forms


class MyForm(forms.Form):
    """<表单说明>"""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        label='名称',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    description = forms.CharField(
        required=False,
        label='描述',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        return name.strip() if name else ''
```

### A.5 定时任务模板

```python
# -*- coding: utf-8 -*-
"""
================================================================================
文件：<task_name>_task.py
路径：<file_path>
================================================================================

功能说明：
    <功能描述>

版本：
    - 1.0: <初始版本>

依赖：
    - core.services.tasks.base: 任务基类
"""

import logging
from core.services.tasks.base import CronTask
from core.services import SettingsService

logger = logging.getLogger(__name__)


class MyTask(CronTask):
    """<任务说明>"""
    
    @property
    def name(self) -> str:
        return "<task_name>"
    
    def is_enabled(self) -> bool:
        return SettingsService.get_setting('<enabled_key>', 'true') == 'true'
    
    def get_interval(self) -> int:
        interval = SettingsService.get_setting('<interval_key>', '3600')
        return int(interval)
    
    def execute(self):
        """执行任务"""
        try:
            logger.info("任务开始...")
            # 业务逻辑
            logger.info("任务完成")
            return "完成"
        except Exception as e:
            logger.error(f"任务失败: {e}")
            return f"失败: {e}"
```

---

## 附录B 反模式（禁止用法）

### B.1 查询相关

```python
# ✗ 禁止：未检查 .first() 返回值
customer = CustomerFields.objects.filter(id=customer_id).first()
print(customer.customer_name)  # 可能抛出 AttributeError

# ✓ 正确：检查返回值
customer = CustomerFields.objects.filter(id=customer_id).first()
if customer:
    print(customer.customer_name)

# ✗ 禁止：N+1 查询问题
customers = CustomerFields.objects.all()
for c in customers:
    print(c.node.created_by.username)  # 每次循环都查询数据库

# ✓ 正确：使用 select_related 预加载
customers = CustomerFields.objects.select_related('node__created_by').all()
for c in customers:
    print(c.node.created_by.username)  # 已预加载

# ✗ 禁止：在循环中执行查询
for user in users:
    CustomerFields.objects.filter(created_by=user).count()  # N 次查询

# ✓ 正确：使用annotate聚合
from django.db.models import Count
users_with_count = User.objects.annotate(
    customer_count=Count('created_nodes')
)
```

### B.2 安全相关

```python
# ✗ 禁止：SQL 注入风险
query = f"SELECT * FROM customers WHERE name = '{name}'"
Cursor.execute(query)

# ✓ 正确：使用参数化查询
CustomerFields.objects.filter(customer_name=name)

# ✗ 禁止：XSS 风险（在模板中未转义）
{{ user_input }}  # 如果是 Jinja2，默认转义
# 但在 Django 模板中需使用 |safe 明确标记

# ✓ 正确：确保转义
{{ user_input }}  # Django 默认转义
# 或 Jinja2 中
{{ user_input|escape }}

# ✗ 禁止：权限检查遗漏
def delete_customer(request, customer_id):
    CustomerService.delete(customer_id)  # 任何人都能删除

# ✓ 正确：添加权限检查
@login_required
def delete_customer(request, customer_id):
    # 权限检查
    if not request.user.is_admin:
        raise PermissionDenied
    CustomerService.delete(customer_id)
```

### B.3 性能相关

```python
# ✗ 禁止：使用大文本字段的 like 查询
CustomerFields.objects.filter(description__contains='关键词')

# ✓ 正确：使用全文搜索或限制范围
CustomerFields.objects.filter(description__icontains='关键词')[:1000]

# ✗ 禁止：频繁调用 SettingsService.get_setting（无缓存）
for i in range(1000):
    value = SettingsService.get_setting('key')  # 每次查询数据库

# ✓ 正确：SettingsService 已有缓存机制，确保使用它

# ✗ 禁止：在模板中进行复杂计算
{% for customer in customers %}
    {{ customer.get_complex_calculation }}  # 每次渲染都计算
{% endfor %}

# ✓ 正确：在视图中预先计算
customers = CustomerFields.objects.all()
for c in customers:
    c.precalculated = c.get_complex_calculation()
```

### B.4 代码风格相关

```python
# ✗ 禁止：过长的函数
def do_everything():  # 500 行函数
    # ... 大量代码
    pass

# ✓ 正确：拆分函数
def do_everything():
    step_one()
    step_two()
    step_three()

# ✗ 禁止：魔法数字
if status == 1:  # 1 是什么？
    pass

# ✓ 正确：使用常量或枚举
class Status:
    PENDING = 1
    ACTIVE = 2
    INACTIVE = 3

if status == Status.ACTIVE:
    pass

# ✗ 禁止：空文件头注释
"""

"""

# ✓ 正确：完整的文件头注释（见第二章）

# ✗ 禁止：混合双引号和单引号（除非必要）
message = "双引号"
message = '单引号'

# ✓ 正确：保持一致
message = "双引号"  # 整个项目保持一致
```

---

## 附录C 与模板规范关联

### C.1 前后端数据传递

```python
# View 层传递数据到模板
def customer_list(request):
    customers = CustomerService.get_list()
    
    return render(request, 'modules/customer/list.html', {
        'customers': customers,              # 主数据
        'customer_types': customer_types,    # 选项数据
        'search': search,                    # 搜索参数
        'filter_type': filter_type,         # 过滤参数
        'pagination': pagination,            # 分页数据
    })
```

### C.2 Jinja2 变量渲染

详见 `A04_模板开发规范.md`，关键区别：

```html
<!-- Django 模板 -->
{{ value|default:"x" }}
{{ value|date:"Y-m-d" }}

<!-- Jinja2 模板 -->
{{ value|default("x") }}        <!-- 注意括号 -->
{{ value|date("Y-m-d") }}       <!-- 注意括号 -->
{{ csrf_token }}                <!-- 注意不是模板标签 -->
```

### C.3 XSS 防护

```python
# 后端确保数据安全
from django.utils.html import escape

def safe_output(value):
    """转义 HTML 特殊字符"""
    return escape(value) if value else ''

# 在模板中 Jinja2 默认自动转义
{{ customer.name }}  # 安全

# 除非明确标记
{{ customer.name|safe }}  # 仅在确定安全时使用
```

---

## 附录D 检查清单

### D.1 代码提交前检查

- [ ] 文件头部注释完整（包含文件、路径、功能、版本、依赖）
- [ ] import 语句分组正确（标准库、第三方、Django、项目内部）
- [ ] 类名、函数名、变量名符合规范
- [ ] `.first()` 查询有 null 检查
- [ ] 外键访问有安全保护（hasattr 或 if 判断）
- [ ] 权限检查到位（@login_required + PermissionService）
- [ ] 静态方法使用 @staticmethod 装饰器
- [ ] 函数有类型注解和文档字符串
- [ ] 无硬编码的魔法数字/字符串
- [ ] 异常处理适当（try-except 或向上抛出）

### D.2 Django 系统检查

```bash
# 运行 Django 系统检查
./venv/bin/python manage.py check

# 运行特定应用检查
./venv/bin/python manage.py check nodes
./venv/bin/python manage.py check core

# 检查数据库迁移
./venv/bin/python manage.py showmigrations

# 检查 URL 配置
./venv/bin/python manage.py show_urls  # 如安装了 django-extensions
```

### D.3 测试运行检查

```bash
# 运行所有测试
./venv/bin/python manage.py test

# 运行特定应用的测试
./venv/bin/python manage.py test core
./venv/bin/python manage.py test nodes

# 运行特定测试类
./venv/bin/python manage.py test core.tests.UserServiceTestCase

# 运行特定测试方法
./venv/bin/python manage.py test core.tests.UserServiceTestCase.test_create_user_empty_password

# 查看测试覆盖率（需安装 coverage）
coverage run ./venv/bin/python manage.py test
coverage report
```

---

## 附录E 相关文档

| 文档 | 说明 |
|------|------|
| **A02_模块技术规范.md** | Node 节点类型系统的实现指南 |
| **A04_模板开发规范.md** | Jinja2 模板语法规范 |
| **A03_省市县联动字段技术规范.md** | 省市区三级联动字段设计 |
| **docs/开发规范.md** | 项目开发通用规范 |
| **docs/bug排查规范.md** | Bug 排查检查清单 |

---

*文档版本：1.1*
*最后更新：2026-05-03*
