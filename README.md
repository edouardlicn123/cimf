# 仙芙 CIMF

<img src="./static/cimf.png" alt="Logo" width="50%">

企业级内部管理系统，AI 开发。v1.754

> CIMF = Corporate Internal Management Framework，企业内部管理框架。

灵感来自 Drupal，通过 node、field、taxonomy 等功能实现 CRM 等系统的管理功能。

---

## 技术栈

| 分类 | 技术 |
|------|------|
| 后端 | Python 3.12 / Django 6.0+ |
| 模板引擎 | Jinja2 3.1+ |
| API | Django REST Framework 3.17+ |
| 数据库 | SQLite（默认）/ MySQL |
| 前端 | Bootstrap 5 + 8 种 CSS 主题 |
| 水印 | Pillow 12+ / PyPDF 4+ |
| 生产部署 | Gunicorn 23+ |

---

## 功能特点

- 🎨 **8 种界面主题** - 默认/中国红/靛蓝/马卡龙/橙红/绿岛森林/踊/梵紫，随时切换
- 📐 **CSS 设计套件** - 基本卡片、基本按键、基本过滤标签、基本列表
- 🔐 **角色权限体系** - 一类/二类/三类用户三级权限管理
- 📦 **模块化节点系统** - 插件式模块架构，支持动态加载/卸载
- 📝 **26 种自定义字段类型** - 文本、数字、布尔、文件、图片、邮箱、电话、日期等
- 🗂️ **词汇表管理** - 预置分类（国家、客户类型、行业、企业性质等）
- 🗺️ **中国行政区划** - 省市县三级联动字段
- 💧 **水印保护** - 网页动态水印 + 导出文件水印
- 📥 **数据导入导出** - 支持 CSV/Excel 格式
- ✉️ **SMTP 邮件系统** - 邮件配置、模板、发送历史
- 📲 **模块市场** - 在线下载安装更多模块
- ⏰ **定时任务系统** - 可扩展的 Cron 任务
- 🏠 **首页快捷入口** - 卡片布局，支持自定义

---

## 目前已有模块

| 模块 | 类型 | 说明 |
|------|------|------|
| 客户信息（海外） | node | 海外客户信息管理 |
| 时钟 | system | 时钟/日历展示 |
| 计算器 | tool | 计算器工具 |
| SMTP 测试 | tool | SMTP 邮件发送测试 |

> 💡 更多模块可通过**模块市场**在线下载安装。

---

## 主题一览

| 主题 | 风格描述 |
|------|----------|
| 默认 | LinkedIn 经典蓝，专业商务 |
| 中国红 | 高饱和红色，浓重热烈 |
| 靛蓝 | 深靛蓝，科技感 |
| 马卡龙 | 柔和低饱和度，削弱视觉冲击 |
| 橙红 | 品牌红橙，清爽商务，B2B 专业感 |
| 绿岛森林 | 暖灰大地调，自然宁静 |
| 踊 | 温暖文艺风，柔和治愈 |
| 梵紫 | 知性紫调，典雅高贵 |

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
