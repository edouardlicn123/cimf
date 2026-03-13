# 水印功能实现技术方案

## 1. 功能概述

本方案实现网页水印功能，用于防止用户截图泄露信息，包含以下特性：
- 登录用户名的水印显示
- 多层防护机制阻止用户移除水印
- 服务端导出文件时添加水印
- 所有功能可在系统设置中配置

## 2. 技术方案

### 2.1 网页水印显示

#### 显示原理
在页面加载时，根据系统设置生成水印DOM元素，覆盖整个页面。

#### 防护机制

| 防护措施 | 实现方式 | 效果 |
|---------|---------|------|
| 提高删除难度 | 多层嵌套span、随机class名、固定定位 | 增加F12删除成本 |
| 控制台检测 | JS定时检测devtools状态 | 检测到时弹窗警告 |
| 快捷键禁用 | 阻止F12、Ctrl+Shift+I等 | 阻止打开开发者工具 |
| 定时检测 | JS定时检查水印是否存在 | 被删除后重新生成 |

#### 显示内容可配置
- `username` - 用户登录名
- `nickname` - 用户昵称
- `email` - 用户邮箱

### 2.2 服务端导出水印

#### CSV导出
在CSV文件内容中追加水印行：
```
# 水印: 用户名 | 导出时间: 2026-01-01 12:00:00
```

#### Excel导出
使用openpyxl在Excel中添加水印文字

### 2.3 页面显示控制

- 登录页 (`auth.login`) - 不显示水印
- 错误页面 (`errors/*.html`) - 显示水印
- 其他页面 - 根据设置显示水印

## 3. 系统设置项

### 3.1 新增设置项

```python
DEFAULT_SETTINGS = {
    # === 网页水印基础设置 ===
    'enable_web_watermark': 'true',        # 是否启用网页水印
    'web_watermark_content': 'username',   # 显示内容: username/nickname/email
    'web_watermark_opacity': '0.15',       # 透明度: 0.1-0.5

    # === 网页水印防护设置 ===
    'enable_watermark_console_detection': 'true',  # 检测控制台打开
    'enable_watermark_shortcut_block': 'true',      # 禁用快捷键

    # === 导出文件水印设置 ===
    'enable_export_watermark': 'true',     # 导出文件是否加水印
}
```

### 3.2 现有设置项（保留）

```python
# 原有的水印相关设置（用于导出文件）
'report_watermark_text': '内部管理系统 - 内部使用',
'report_watermark_opacity': '0.3',
```

## 4. 文件结构

### 4.1 新增文件

| 文件路径 | 说明 |
|---------|------|
| `app/templates/includes/watermark.html` | 水印HTML模板 |
| `app/static/css/watermark.css` | 水印样式 |
| `app/static/js/watermark.js` | 水印防护JS |

### 4.2 修改文件

| 文件路径 | 修改内容 |
|---------|---------|
| `app/services/settings_service.py` | 添加新设置项 |
| `app/forms/admin_forms.py` | 添加表单字段 |
| `app/templates/admin/system_settings.html` | 添加水印设置卡片 |
| `app/templates/base.html` | 引入水印模板 |
| `app/templates/auth/login.html` | 隐藏水印 |
| `app/routes/export.py` | 导出文件添加水印 |

## 5. 实施步骤

### Step 1: 添加系统设置 (settings_service.py)
- 添加8个新设置项到DEFAULT_SETTINGS
- 添加注释说明分组

### Step 2: 添加表单字段 (admin_forms.py)
- enable_web_watermark (BooleanField)
- web_watermark_content (SelectField)
- web_watermark_opacity (FloatField)
- enable_watermark_console_detection (BooleanField)
- enable_watermark_shortcut_block (BooleanField)
- enable_export_watermark (BooleanField)

### Step 3: 创建水印样式 (watermark.css)
- watermark-container: 固定定位全屏
- watermark-item: 旋转45度、半透明
- 响应式设计

### Step 4: 创建水印模板 (watermark.html)
- 根据设置生成水印内容
- 多层嵌套span元素
- 循环生成足够覆盖屏幕的水印

### Step 5: 创建防护JS (watermark.js)
- console检测函数
- 快捷键禁用函数
- 定时检查函数

### Step 6: 修改系统设置页面 (system_settings.html)
- 创建水印设置卡片
- 整合所有水印相关设置

### Step 7: 修改base.html
- 引入水印模板
- 引入水印JS
- 登录页不显示水印

### Step 8: 修改登录页 (login.html)
- 设置hide_watermark变量

### Step 9: 修改导出功能 (export.py)
- CSV导出添加水印注释
- Excel导出添加水印（预留）

## 6. 技术限制说明

### 无法完全阻止的情况
1. 用户使用外部截图工具（而非浏览器截图）
2. 用户使用自动化脚本/无头浏览器
3. 用户拍照屏幕

### 可防护的情况
1. 普通用户无意间截图
2. 简单尝试删除水印
3. 尝试使用快捷键打开开发者工具

## 7. 后续可扩展

1. **图片水印** - 上传图片时自动添加水印
2. **PDF水印** - 导出PDF时添加水印
3. **IP记录** - 截图时记录用户IP
4. **数字水印** - 隐水印技术更难去除

## 8. 测试清单

- [ ] 登录后页面显示用户名水印
- [ ] 透明度设置生效
- [ ] 显示内容(username/nickname/email)切换生效
- [ ] F12快捷键被阻止
- [ ] 控制台打开时显示警告
- [ ] 水印删除后自动重新生成
- [ ] 登录页不显示水印
- [ ] 错误页面显示水印
- [ ] 导出CSV包含水印信息
- [ ] 系统设置保存水印配置生效
