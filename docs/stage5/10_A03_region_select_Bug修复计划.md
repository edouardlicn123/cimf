# A03 — `region_select.py` Bug 修复计划

> 发现于 2026-07-22 技术规范审计
> 对应文档：`docs/技术规范/A03_省市县联动字段技术规范.md`
> 预计工作量：~10 行 Python + ~140 行已有 JS（确认路径）

---

## 1. Bug 清单

| # | 严重度 | 文件 | 行 | 根因 | 影响 |
|:-:|:------:|------|:--:|------|------|
| 1 | 🔴 P0 | `core/fields/region_select.py` | 41-43 | URL reverse 命名空间错误 | `RegionSelectField` 渲染时 `NoReverseMatch` → 500 |
| 2 | 🟡 P2 | `core/fields/region_select.py` | 71 | Media JS 路径缺 `STATIC_URL` 前缀 | 浏览器请求 `/js/region_select.js`（404），非 `/static/js/region_select.js` |

---

## 2. 详细分析

### Bug 1：URL Reverse 命名空间（P0）

**代码现状：**
```python
province_api = reverse("core:api_regions_provinces")    # 行 41
city_api = reverse("core:api_regions_cities")            # 行 42
district_api = reverse("core:api_regions_districts")     # 行 43
```

**路由配置（`core/api_urls.py`）：**
```python
app_name = "api"                                          # 行 24
path("regions/provinces/", ..., name="api_regions_provinces")   # 行 36
```

**根因：** `region_select.py` 中的 `reverse` 使用 `core:api_...` 命名空间，但 `api_urls.py` 的 `app_name` 为 `"api"`（而非 `"core"`）。正确的命名空间是 `api:`（即 `reverse("api:api_regions_provinces")`）。

**为什么文档按现状更新：** 文档 A03 §9.1 已正确写 `url('api:api_regions_provinces')`，因此文档与代码之间的差异仅在于代码中的 Bug。

**触发条件：** 任何使用 `RegionSelectField` 的表单页面，在 `render()` 被调用时立即触发。由于该字段用于 `modules/customer/`（客户管理模块），在打开客户表单页面时会出现 500 错误。

### Bug 2：Media JS 路径（P2）

**代码现状：**
```python
class Media:
    js = ("/js/region_select.js",)    # 行 71 — 绝对路径
```

**实际静态文件：** `static/js/region_select.js`（已存在且功能完整，136 行）

**配置（`settings.py`）：**
```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

**根因：** `Media` 类中的 `js` 路径以 `/` 开头，Django 将其视为**绝对 URL**（不追加 `STATIC_URL`）。正确写法应为相对路径：

```python
js = ("js/region_select.js",)    # Django 自动解析为 /static/js/region_select.js
```

或使用 `"region_select/js/region_select.js"` 做命名空间隔离。

**JS 文件状态：** `static/js/region_select.js` 已完整实现（依赖 `window.FFE.apiGet`，由 `static/js/common.js` 提供），无需额外编写。

---

## 3. 修复方案

### 文件修改清单

| 文件 | 变更 | 行数变化 |
|------|------|:--------:|
| `core/fields/region_select.py` | 3 行 `reverse` 命名空间 + 1 行 JS 路径 | 0（仅修改） |
| `static/js/region_select.js` | 无需修改 | — |

### 3.1 `region_select.py` 修改

**变更 1-3：URL 命名空间修正**
```python
# 修改前                      # 修改后
reverse("core:api_regions_")  →  reverse("api:api_regions_")
```

**变更 4：Media JS 路径**
```python
# 修改前                        # 修改后
js = ("/js/region_select.js",)  →  js = ("js/region_select.js",)
```

### 3.2 文案更新

`region_select.py` 头部文档字符串中如果提到 URL，一并更新。

### 3.3 A03 文档更新

Bug 修复后，A03 文档需同步修改：
- §6.1: `region_select.js` 标记"待实现"→ 改为"已实现"
- §14: 文件清单中 `region_select.js` 的 ⚠️ 移除
- §7 测试页面：如果页面已实现更新状态
- 修复日期和版本号

---

## 4. 验证方法

| 检查项 | 方法 | 预期结果 |
|--------|------|----------|
| 命名空间 | `./venv/bin/python -c "from django.urls import reverse; print(reverse('api:api_regions_provinces'))"` | `/api/v1/regions/provinces/` |
| JS 路径 | `./venv/bin/python -c "from core.fields.region_select import RegionSelectWidget; print(RegionSelectWidget.Media.js)"` | `('js/region_select.js',)` |
| 渲染不抛异常 | `./venv/bin/python manage.py shell -c "from core.fields.region_select import RegionSelectField; f = RegionSelectField(); print(f.widget.render('test', ''))"` | 正常输出 HTML |
| 实际页面 | 打开客户编辑页面，检查浏览器网络请求 | `/static/js/region_select.js` 200 |
| 级联功能 | 测试省→市→区三级联动 | 每级正确加载下一级 |

---

## 5. 关联修改

无。Bug 范围局限在 `region_select.py` 一个文件的 4 行更改。

---

## 6. 修复后文档同步

| 文档 | 变更内容 |
|------|----------|
| `docs/技术规范/A03_省市县联动字段技术规范.md` | §6.3/§7/§14 更新 `region_select.js` 状态；版本号 1.3→1.4 |
