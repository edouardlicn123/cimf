# core/forms 表单与验证规范

> 文档版本：1.5  
> 创建日期：2026-04-07  
> 最后更新：2026-05-06

---

## 一、概述

### 1.1 模块定位

表单层（Forms）是 Django 的数据验证和渲染核心，负责接收用户输入、进行数据验证、生成表单 HTML。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **服务端验证** | 所有验证逻辑必须在服务端执行，不依赖客户端验证 |
| **字段级验证** | 使用 `clean_<fieldname>()` 方法进行字段级验证 |
| **表单级验证** | 使用 `clean()` 方法进行跨字段验证 |
| **Widget 统一** | 使用 Bootstrap 5 样式类（form-control, form-select 等） |
| **BootstrapFormMixin** | 使用 `core.forms.mixins.BootstrapFormMixin` 自动为表单字段添加 Bootstrap 样式，无需手动设置 widget attrs |

### 1.3 表单分布

| 文件 | 表单类 | 用途 |
|------|--------|------|
| `mixins.py` | BootstrapFormMixin | Bootstrap 样式混合类 |
| `auth_forms.py` | LoginForm | 登录表单 |
| `admin_forms.py` | UserCreateForm, UserEditForm, UserSearchForm, SystemSettingsForm, PermissionForm | 后台管理 |
| `settings_forms.py` | ProfileForm, PreferencesForm, ChangePasswordForm | 用户设置 |

---

## 二、表单清单

### 2.1 auth_forms.py

#### LoginForm - 登录表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| username | CharField | max_length=64, min_length=3 | TextInput |
| password | CharField | 无 | PasswordInput |
| remember_me | BooleanField | required=False | CheckboxInput |

**字段级验证**：
- `clean_username()`: 去除用户名首尾空格

### 2.2 admin_forms.py

#### UserSearchForm - 用户搜索表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| username | CharField | max_length=64, required=False | TextInput |
| is_active | BooleanField | required=False, initial=True | CheckboxInput |

#### UserCreateForm - 用户创建表单

> 继承 `BootstrapFormMixin` 和 `forms.ModelForm`，自动应用 Bootstrap 样式。

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| username | CharField | 来自 Meta.fields | TextInput |
| nickname | CharField | 来自 Meta.fields | TextInput |
| email | EmailField | 来自 Meta.fields | EmailInput |
| role | CharField | 来自 Meta.fields, choices=UserRole.CHOICES | Select |
| is_admin | BooleanField | 来自 Meta.fields | CheckboxInput |
| password | CharField | min_length=10, **required** | PasswordInput |
| confirm_password | CharField | min_length=10, **required** | PasswordInput |

**字段级验证**：
- `clean_username()`: 检查用户名唯一性
- `clean_email()`: 检查邮箱唯一性

**表单级验证**：
- `clean()`: 检查两次密码一致，密码长度 >= 10

#### UserEditForm - 用户编辑表单

> 继承 `BootstrapFormMixin` 和 `forms.ModelForm`，自动应用 Bootstrap 样式。

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| username | CharField | 来自 Meta.fields, **readonly** | TextInput |
| nickname | CharField | 来自 Meta.fields | TextInput |
| email | EmailField | 来自 Meta.fields | EmailInput |
| role | CharField | 来自 Meta.fields, choices=UserRole.CHOICES | Select |
| is_admin | BooleanField | 来自 Meta.fields | CheckboxInput |
| is_active | BooleanField | 来自 Meta.fields | CheckboxInput |
| password | CharField | min_length=10, **required=False** | PasswordInput |

**特殊处理**：
- `__init__()`: 接收 `user_id` 参数用于唯一性验证
- `clean_username()`: 用户名不可修改，只验证唯一性

#### SystemSettingsForm - 系统设置表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| system_name | CharField | max_length=60 | TextInput |
| upload_max_size_mb | IntegerField | min_value=5, max_value=1024 | NumberInput |
| upload_max_files | IntegerField | min_value=5, max_value=500 | NumberInput |
| session_timeout_minutes | IntegerField | min_value=5, max_value=1440 | NumberInput |
| enable_audit_log | BooleanField | required=False | CheckboxInput |
| enable_web_watermark | BooleanField | required=False | CheckboxInput |
| web_watermark_opacity | FloatField | min_value=0.05, max_value=0.5, required=False | NumberInput |
| enable_export_watermark | BooleanField | required=False | CheckboxInput |
| time_zone | ChoiceField | choices | Select |

#### PermissionForm - 权限编辑表单
（预留，当前为空）

### 2.3 settings_forms.py

#### ProfileForm - 个人信息表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| nickname | CharField | max_length=64, required=False | TextInput |
| email | EmailField | required=False | EmailInput |

**特殊处理**：
- `__init__()`: 接收 `user_id` 参数用于唯一性验证
- `clean_email()`: 检查邮箱唯一性（排除当前用户）

#### PreferencesForm - 偏好设置表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| theme | ChoiceField | choices | Select |
| notifications_enabled | BooleanField | required=False, initial=True | CheckboxInput |
| preferred_language | ChoiceField | choices | Select |

**选项**（引用 `core.constants`）：
```python
from core.constants import UserTheme, Language

# UserTheme.DISPLAY_LABELS:
# {
#     'default': '默认',
#     'gov': '政府风格 - 酒红配色、沉稳',
#     'indigo': '靛蓝风格 - 专业沉稳，科技感',
#     'savawoku': 'Savawoku - 品牌红橙、专业商务',
#     'macaron': '马卡龙风格 - 削弱视觉冲击',
#     'teal': '青绿风格 - 清新现代',
#     'uniklo': 'uniklo - 干净线条、经典红白',
# }

# Language.CHOICES:
# [('zh', '中文（简体）'), ('en', 'English')]
```

#### ChangePasswordForm - 修改密码表单

| 字段 | 类型 | 验证规则 | Widget |
|------|------|----------|--------|
| current_password | CharField | **required** | PasswordInput |
| new_password | CharField | min_length=10, **required** | PasswordInput |
| confirm_password | CharField | min_length=10, **required** | PasswordInput |

**特殊处理**：
- `__init__()`: 接收 `user` 参数用于验证当前密码
- `clean_current_password()`: 验证当前密码是否正确

**表单级验证**：
- `clean()`: 检查两次新密码一致，密码长度 >= 10

---

## 三、验证规范

### 3.1 字段级验证

使用 `clean_<fieldname>()` 方法：

```python
def clean_username(self):
    username = self.cleaned_data.get('username')
    if username:
        username = username.strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError('该用户名已被占用')
    return username
```

### 3.2 表单级验证

使用 `clean()` 方法：

```python
def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    
    if password and confirm_password:
        if password != confirm_password:
            raise ValidationError('两次输入的密码不一致')
        if len(password) < 10:
            raise ValidationError('密码长度至少 10 个字符')
    
    return cleaned_data
```

### 3.3 验证顺序

1. 字段清洗（`clean_<fieldname>()`）
2. 表单清洗（`clean()`）
3. 如果需要，在视图中调用服务层验证

---

## 四、Widget 规范

### 4.1 常用 Widget 类

| 输入类型 | Widget | Bootstrap 类 |
|----------|--------|--------------|
| 文本输入 | TextInput | form-control form-control-lg |
| 邮箱输入 | EmailInput | form-control form-control-lg |
| 密码输入 | PasswordInput | form-control form-control-lg |
| 数字输入 | NumberInput | form-control form-control-lg |
| 下拉选择 | Select | form-select form-select-lg |
| 复选框 | CheckboxInput | form-check-input |
| 开关 | CheckboxInput + role=switch | form-check-input |

### 4.2 Widget 属性示例

```python
widget=forms.TextInput(attrs={
    'class': 'form-control form-control-lg',
    'placeholder': '提示文字',
    'autocomplete': 'username',
})

widget=forms.CheckboxInput(attrs={
    'class': 'form-check-input',
    'role': 'switch',
})
```

---

## 五、表单在视图中的使用

### 5.1 GET 请求 - 渲染空表单

```python
def user_create(request):
    if request.method == 'POST':
        # ...
    
    form = UserCreateForm()
    return render(request, 'admin/system_user_edit.html', {
        'form': form,
        'is_create': True,
    })
```

### 5.2 POST 请求 - 处理表单提交

```python
def user_create(request):
    if request.method == 'GET':
        form = UserCreateForm()
        return render(request, 'admin/system_user_edit.html', {
            'form': form,
            'is_create': True,
        })
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            # 获取验证后的数据
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 调用服务层创建用户
            UserService.create_user(...)
            return redirect('core:system_users')
        
        return render(request, 'admin/system_user_edit.html', {
            'form': form,
            'is_create': True,
        })
```

---

## 六、错误消息规范

### 6.1 ValidationError 使用

```python
from django.core.exceptions import ValidationError

# 字段级错误
raise ValidationError('该用户名已被占用，请更换其他用户名')

# 表单级错误
raise ValidationError('两次输入的密码不一致')
```

### 6.2 模板中显示错误

```html
{{ form.username.errors }}
{% if form.username.errors %}
    <div class="invalid-feedback d-block">
        {{ form.username.errors.0 }}
    </div>
{% endif %}
```

---

## 七、待补充

- [ ] 补充表单测试规范
- [ ] 添加自定义 Widget 示例
- [ ] 补充表单安全最佳实践

---

## 八、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-04-07 | 初始版本 |
| 1.1 | 2026-05-03 | 修正 UserCreateForm 字段（移除 is_active） |
| 1.2 | 2026-05-06 | 全面审查，确认与代码一致 |
| 1.3 | 2026-05-06 | 修正 UserCreateForm/UserEditForm 继承类：forms.Form→forms.ModelForm |
| 1.4 | 2026-05-06 | 补充 mixins.py（BootstrapFormMixin）到表单分布表 |
