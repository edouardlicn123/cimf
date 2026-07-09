# 修复 /nodes/customer/create/ 模板不存在 Bug

## 根因分析

`core/node/urls.py` 中 create/delete 路由指向硬编码的核心视图（`node_create`/`node_delete`），而 list/view/edit 已通过 `module_dispatch` 动态分发到模块视图。

| 路由 | 当前处理 | 状态 |
|------|----------|------|
| `/nodes/<slug>/` | `module_dispatch` → `customer.views.node_list` | ✓ |
| `/nodes/<slug>/<id>/` | `module_dispatch` → `customer.views.node_view` | ✓ |
| `/nodes/<slug>/<id>/edit/` | `module_dispatch` → `customer.views.node_edit` | ✓ |
| `/nodes/<slug>/create/` | `node_create` → 渲染 `node/node_edit.html` | ✗ 模板不存在 |
| `/nodes/<slug>/<id>/delete/` | `node_delete` → 直接删除逻辑 | ✓ 能工作但不统一 |

## 修复方案：扩展 `module_dispatch` 统一接管

### 文件 1: `core/node/urls.py`

将 create/delete 路由改为指向 `module_dispatch`，通过 `kwargs` 传递 action 参数：

```python
urlpatterns = [
    path('dashboard/', views.nodes_index, name='index'),
    path('<slug:node_type_slug>/create/', views.module_dispatch, name='node_create', kwargs={'action': 'create'}),
    path('<slug:node_type_slug>/<int:node_id>/', views.module_dispatch, name='node_view'),
    path('<slug:node_type_slug>/<int:node_id>/edit/', views.module_dispatch, name='node_edit'),
    path('<slug:node_type_slug>/<int:node_id>/delete/', views.module_dispatch, name='node_delete', kwargs={'action': 'delete'}),
    path('<slug:node_type_slug>/', views.module_dispatch, name='module_page'),
]
```

### 文件 2: `core/node/views.py` — `module_dispatch` 函数

增加 `action` 参数支持 create/delete 分发：

```python
@login_required
def module_dispatch(request, node_type_slug: str, node_id: int = None, action: str = None):
    """模块分发视图 - 根据节点类型动态加载对应模块的视图"""
    from django.urls import reverse
    module_path = node_type_slug
    
    try:
        module_views = __import__(f'modules.{module_path}.views', fromlist=[''])
        
        # 新增：create 操作
        if action == 'create':
            if hasattr(module_views, 'node_create'):
                return module_views.node_create(request)
            elif hasattr(module_views, 'create'):
                return module_views.create(request)
            # fallback: 仍然使用旧的核心视图（但会报模板不存在的错）
            return node_create(request, node_type_slug)
        
        # 新增：delete 操作
        if action == 'delete':
            if hasattr(module_views, 'node_delete'):
                return module_views.node_delete(request, node_id)
            elif hasattr(module_views, 'delete'):
                return module_views.delete(request, node_id)
            # fallback: 仍然使用旧的核心视图
            return node_delete(request, node_type_slug, node_id)
        
        # 原有逻辑：list/view/edit
        if hasattr(module_views, 'module_view'):
            return module_views.module_view(request, node_id)
        elif hasattr(module_views, 'detail_view') and node_id:
            return module_views.detail_view(request, node_id)
        elif hasattr(module_views, 'list_view'):
            return module_views.list_view(request)
        elif hasattr(module_views, 'node_list') and not node_id:
            return module_views.node_list(request)
        elif hasattr(module_views, 'node_view') and node_id:
            return module_views.node_view(request, node_id)
        elif hasattr(module_views, 'node_edit') and node_id:
            return module_views.node_edit(request, node_id)
    except ImportError:
        pass
    
    return redirect('node:module_page', node_type_slug)
```

### 预期效果

修改后 `/nodes/customer/create/` 的请求链路：

```
URL: /nodes/customer/create/
  → module_dispatch(slug='customer', action='create')
    → __import__('modules.customer.views')
      → hasattr(module_views, 'node_create') = True
        → customer.views.node_create(request)  ← 使用模块自己的视图和模板
```

### 验证步骤

1. `manage.py check`
2. 访问 `/nodes/customer/create/` 应正常渲染 `edit.html`（customer 模块模板）
3. 验证 customer 列表页的"新建"按钮功能
4. 验证删除按钮功能正常
