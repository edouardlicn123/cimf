# 仙芙CIMF

<img src="./static/cimf.png" alt="Logo" width="50%">

企业级内部管理系统，AI开发。

> CIMF = Corporate Internal Management Framework，企业内部管理框架。

灵感来自 Drupal，通过 node、field、taxonomy 等功能实现 CRM 等系统的管理功能。

---

## 功能特点

- 🔐 **角色权限体系** - 经理/组长/员工三级权限管理，可精细控制节点操作权限
- 📊 **模块化节点系统** - 插件式模块架构，支持动态加载/卸载
- 📝 **24种自定义字段类型** - 文本、数字、布尔、文件、图片、邮箱、电话、日期、地理位置、颜色、身份识别、隐私脱敏等
- 🗂️ **词汇表管理** - 预置分类（国家、客户类型、行业、企业性质、客户等级等）
- 🗺️ **中国行政区划** - 省市县三级联动字段，支持级联选择
- 💧 **水印保护** - 网页动态水印 + 导出文件水印
- 📥 **数据导入导出** - 支持 CSV/Excel 格式，可自定义字段和过滤条件
- ⏰ **定时任务系统** - 可扩展的 Cron 任务（时间同步、缓存清理）
- 🧪 **完整测试覆盖** - 核心模块单元测试和集成测试
- 🏠 **首页快捷入口** - 3×2 卡片布局，支持拖拽自定义

---

## 目前已有模块

| 模块 | 类型 | 说明 |
|------|------|------|
| 客户信息（海外） | node | 海外客户信息管理，支持 20+ 字段，含 LinkedIn |
| 客户信息（国内） | node | 国内客户信息管理，支持省市县联动、微信/钉钉 |
| 时钟 | system | 时钟/日历展示，仪表盘快捷卡片 |

---

## 快速开始

```bash
./run.sh
```

选择「1. 启动服务」默认运行在 http://localhost:8000  
默认账号：`admin` / `admin123`

---

## 开发命令

```bash
# 启动服务
./run.sh

# 运行测试
./venv/bin/python manage.py test

# 创建迁移
./venv/bin/python manage.py makemigrations

# 执行迁移
./venv/bin/python manage.py migrate

# Django 系统检查
./venv/bin/python manage.py check

# 创建超级用户
./venv/bin/python manage.py createsuperuser
```

---

## 许可证

MIT License

Copyright (c) 2024-2026 Xianfu CIMF

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
