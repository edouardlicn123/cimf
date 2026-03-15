# 10_统一Cron调度服务指引.md

## 文档信息

- **版本**: 1.3
- **创建日期**: 2026-03-14
- **更新日期**: 2026-03-14
- **状态**: 已完成
- **前置文档**: 09_系统性能优化与时钟同步服务指引.md

---

## 1. 背景与目标

### 1.1 现有问题

在 09 文档中实现了 TimeSyncService，但其内部维护自己的后台线程来执行时间同步任务。这种方式存在以下问题：

| 问题 | 描述 |
|------|------|
| 线程分散 | 每个任务都需要单独的线程管理 |
| 难以扩展 | 新增任务需要在服务内新建线程 |
| 监控困难 | 难以统一查看所有任务的状态 |
| 配置分散 | 任务的间隔配置分散在不同服务中 |

### 1.2 设计目标

创建一个统一的 Cron 服务框架：

1. **统一的任务调度器** - 管理所有后台定时任务
2. **可扩展的任务注册** - 轻松添加新任务
3. **系统设置配置** - 任务间隔通过系统设置管理
4. **统一的生命周期** - 启动/停止/重启
5. **任务状态监控** - 统一的 API 查看所有任务状态

---

## 2. 系统架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         Flask 应用                            │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   CronService (调度器)                   │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Task Registry (任务注册表)          │  │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐    │  │  │
│  │  │  │  TimeSyncTask   │  │ CacheCleanupTask │    │  │  │
│  │  │  │  每15分钟        │  │  每5分钟         │    │  │  │
│  │  │  └─────────────────┘  └─────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                        │                               │  │
│  │                        ▼                               │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │            后台调度线程 (单线程)                   │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                      API 层                            │  │
│  │  GET /api/cron/status  - 获取所有任务状态             │  │
│  │  POST /api/cron/run/<name> - 手动触发任务             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 |
|------|------|
| CronService | 任务调度器，管理所有任务的注册、启动、停止 |
| CronTask | 任务基类，定义任务接口 |
| TimeSyncTask | 时间同步任务，继承 CronTask |
| CacheCleanupTask | 缓存清理任务，继承 CronTask |
| TimeSyncService | 提供时间同步的具体实现（被任务调用） |

---

## 3. 数据库设计

### 3.1 系统设置扩展

新增以下配置项：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| cron_time_sync_enabled | bool | true | 时间同步任务开关 |
| cron_time_sync_interval | int | 900 | 时间同步间隔（秒，默认15分钟） |
| cron_cache_cleanup_enabled | bool | true | 缓存清理任务开关 |
| cron_cache_cleanup_interval | int | 300 | 缓存清理间隔（秒，默认5分钟） |

---

## 4. 代码实现

### 4.1 文件结构

```
app/
└── services/
    └── core/
        ├── cron_service.py           # 新增：统一调度服务
        ├── time_sync_service.py      # 修改：移除内部线程
        └── tasks/
            ├── __init__.py          # 新增：任务模块
            ├── base.py              # 新增：任务基类
            ├── time_sync_task.py    # 新增：时间同步任务
            └── cache_cleanup_task.py # 新增：缓存清理任务
```

### 4.2 任务基类

```python
# 文件路径：app/services/core/tasks/base.py
# 功能说明：定时任务基类
# 版本：1.1
# 更新日期：2026-03-14

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CronTask(ABC):
    """定时任务基类"""

    name: str = "task"
    default_interval: int = 60
    enabled_by_default: bool = True

    def __init__(self):
        self._last_run: Optional[datetime] = None
        self._last_status: str = 'never'
        self._last_error: Optional[str] = None
        self._run_count: int = 0
        self._app_ready: bool = False  # 应用是否就绪

    def set_app_ready(self, ready: bool = True):
        """设置应用是否就绪"""
        self._app_ready = ready

    @property
    @abstractmethod
    def setting_key_enabled(self) -> str:
        """获取启用设置项的 key"""
        pass

    @property
    @abstractmethod
    def setting_key_interval(self) -> str:
        """获取间隔设置项的 key"""
        pass

    def is_enabled(self) -> bool:
        """是否启用此任务"""
        if not self._app_ready:
            return False
        
        try:
            from app.services.core.settings_service import SettingsService
            setting = SettingsService.get_setting(self.setting_key_enabled)
            return setting is None or setting is True or setting == 'true'
        except Exception as e:
            logger.warning(f"任务 {self.name} 检查启用状态失败: {e}")
            return self.enabled_by_default

    def get_interval(self) -> int:
        """获取执行间隔（秒）"""
        if not self._app_ready:
            return self.default_interval
        
        try:
            from app.services.core.settings_service import SettingsService
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval and isinstance(interval, int):
                return interval
        except Exception as e:
            logger.warning(f"任务 {self.name} 获取间隔失败: {e}")
        return self.default_interval

    @abstractmethod
    def execute(self):
        """执行任务逻辑"""
        pass

    def run(self):
        """运行任务（包含异常处理）"""
        if not self._app_ready:
            return
        
        if not self.is_enabled():
            return

        try:
            self.execute()
            self._last_status = 'success'
            self._last_error = None
        except Exception as e:
            self._last_status = 'failed'
            self._last_error = str(e)
        finally:
            self._last_run = datetime.now()
            self._run_count += 1

    def get_status(self) -> dict:
        """获取任务状态"""
        return {
            'name': self.name,
            'enabled': self.is_enabled(),
            'interval': self.get_interval(),
            'app_ready': self._app_ready,
            'last_run': self._last_run.strftime('%Y-%m-%d %H:%M:%S') if self._last_run else None,
            'last_status': self._last_status,
            'last_error': self._last_error,
            'run_count': self._run_count,
        }
```

### 4.3 时间同步任务

```python
# 文件路径：app/services/core/tasks/time_sync_task.py
# 功能说明：时间同步任务

from app.services.core.tasks.base import CronTask


class TimeSyncTask(CronTask):
    """时间同步任务"""

    name = "time_sync"
    default_interval = 900

    @property
    def setting_key_enabled(self) -> str:
        return "enable_time_sync"

    @property
    def setting_key_interval(self) -> str:
        return "time_sync_interval"

    def get_interval(self) -> int:
        """获取执行间隔（秒）- 从分钟转换"""
        interval = super().get_interval()
        return interval * 60

    def execute(self):
        """执行时间同步"""
        from app.services.core.time_sync_service import get_time_sync_service
        time_sync = get_time_sync_service()
        time_sync.sync_time()
```

### 4.4 缓存清理任务

```python
# 文件路径：app/services/core/tasks/cache_cleanup_task.py

from app.services.core.tasks.base import CronTask
import logging

logger = logging.getLogger(__name__)


class CacheCleanupTask(CronTask):
    """缓存清理任务"""

    name = "cache_cleanup"
    default_interval = 300

    @property
    def setting_key_enabled(self) -> str:
        return "cron_cache_cleanup_enabled"

    @property
    def setting_key_interval(self) -> str:
        return "cron_cache_cleanup_interval"

    def execute(self):
        """执行缓存清理"""
        from app.services.core.settings_service import SettingsService
        SettingsService.clear_cache()
        logger.info("缓存清理任务执行完成")
```

### 4.5 Cron 服务

```python
# 文件路径：app/services/core/cron_service.py
# 功能说明：统一的定时任务调度服务
# 版本：1.1
# 更新日期：2026-03-14

import time
import logging
import threading
from typing import Optional, Dict, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from flask import Flask
    from app.services.core.tasks.base import CronTask

logger = logging.getLogger(__name__)


class CronService:
    """统一的定时任务调度服务"""

    def __init__(self, app: Optional['Flask'] = None):
        self._tasks: Dict[str, 'CronTask'] = {}
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        self._app: Optional['Flask'] = app

    def init_app(self, app: 'Flask'):
        """初始化 Flask 应用"""
        self._app = app

    def register(self, task: 'CronTask'):
        """注册任务"""
        self._tasks[task.name] = task
        logger.info(f"任务已注册: {task.name}")

    def unregister(self, task_name: str):
        """注销任务"""
        if task_name in self._tasks:
            del self._tasks[task_name]
            logger.info(f"任务已注销: {task_name}")

    def get_task(self, task_name: str) -> Optional['CronTask']:
        """获取任务"""
        return self._tasks.get(task_name)

    def _run_loop(self):
        """调度循环"""
        logger.info("Cron 服务已启动，等待应用就绪...")
        
        # 等待应用就绪
        while self._running and not self._app:
            time.sleep(1)
        
        logger.info("Cron 服务开始执行任务")

        while self._running:
            try:
                now = time.time()
                tasks_to_run = list(self._tasks.values())

                for task in tasks_to_run:
                    try:
                        # 在 app context 中执行任务
                        with self._app.app_context():
                            if not task.is_enabled():
                                continue

                            if task._last_run is None:
                                logger.info(f"首次执行任务: {task.name}")
                                task.run()
                                logger.info(f"任务完成: {task.name}, 状态: {task._last_status}")
                            else:
                                next_run = task._last_run.timestamp() + task.get_interval()

                                if now >= next_run:
                                    logger.info(f"执行任务: {task.name}")
                                    task.run()
                                    logger.info(f"任务完成: {task.name}, 状态: {task._last_status}")
                    except Exception as task_error:
                        logger.error(f"任务 {task.name} 执行异常: {task_error}", exc_info=True)

            except Exception as e:
                logger.error(f"Cron 调度循环异常: {e}", exc_info=True)

            time.sleep(1)

        logger.info("Cron 服务已停止")

    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("Cron 服务已在运行中")
            return

        self._running = True
        self._start_time = datetime.now()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Cron 后台线程已启动")

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Cron 服务已停止")

    def set_app_ready(self, ready: bool = True):
        """设置所有任务应用已就绪"""
        for task in self._tasks.values():
            task.set_app_ready(ready)
        logger.info(f"Cron 任务应用就绪状态: {ready}")

    def get_status(self) -> dict:
        """获取所有任务状态"""
        return {
            'running': self._running,
            'start_time': self._start_time.strftime('%Y-%m-%d %H:%M:%S') if self._start_time else None,
            'tasks': {name: task.get_status() for name, task in self._tasks.items()},
        }

    def trigger(self, task_name: str) -> dict:
        """手动触发任务"""
        task = self.get_task(task_name)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_name}'}

        if not task.is_enabled():
            return {'success': False, 'error': f'任务未启用: {task_name}'}

        task.run()
        return {
            'success': True,
            'task': task_name,
            'status': task._last_status,
            'last_run': task._last_run.strftime('%Y-%m-%d %H:%M:%S') if task._last_run else None,
        }


_cron_service: Optional[CronService] = None


def get_cron_service() -> CronService:
    """获取 Cron 服务单例"""
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service
```
    """获取 Cron 服务单例"""
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service
```

### 4.6 TimeSyncService 修改

```python
# 文件路径：app/services/core/time_sync_service.py
# 修改说明：移除内部线程管理，仅保留时间同步逻辑

# 移除以下内容：
# - _sync_thread
# - _running
# - _sync_loop()
# - start()
# - stop()

# 保留以下内容：
# - sync_time()
# - get_current_time()
# - get_status()
# - 各种配置获取方法
```

### 4.7 Flask 应用修改

```python
# 文件路径：app/__init__.py
# 修改说明：启动时初始化 Cron 服务

# ── 10. 数据库初始化（根据配置模式） ─────────────────────────────────────────────
init_database(app)

# ── 11. 初始化 Cron 调度服务 ─────────────────────────────────────────────
from app.services.core.cron_service import get_cron_service
from app.services.core.tasks import TimeSyncTask, CacheCleanupTask

cron = get_cron_service()
cron.init_app(app)  # 传入 app 以便在后台线程中使用 app context
cron.register(TimeSyncTask())
cron.register(CacheCleanupTask())
cron.start()
cron.set_app_ready(True)  # 立即启用任务
app.logger.info("Cron 调度服务已启动")

app.logger.info("FFE 项目跟进系统 - 应用初始化完成")
return app
```

### 4.8 重要说明

#### 4.8.1 Flask App Context 问题

后台线程无法继承 Flask 应用的 context，因此需要：

1. **CronService 接收 app** - 通过 `init_app(app)` 方法传入 Flask 实例
2. **任务在 app context 中执行** - 在 `_run_loop` 中使用 `with self._app.app_context():`
3. **应用就绪标志** - 使用 `_app_ready` 标志确保应用完全初始化后才执行任务

#### 4.8.2 初始化顺序

正确的初始化顺序：

1. 数据库初始化 (`init_database(app)`)
2. Cron 服务初始化并传入 app
3. 任务注册
4. 启动 Cron 后台线程
5. 设置任务就绪标志 (`set_app_ready(True)`)
6. 返回 app

### 4.8 API 端点

```python
# 文件路径：app/modules/core/cron/routes.py
# 新增文件

from flask import Blueprint, jsonify, request
from app.services.core.cron_service import get_cron_service

cron_bp = Blueprint('cron', __name__, url_prefix='/api/cron')


@cron_bp.route('/status', methods=['GET'])
def cron_status():
    """获取所有任务状态"""
    cron = get_cron_service()
    return jsonify(cron.get_status())


@cron_bp.route('/run/<task_name>', methods=['POST'])
def cron_run_task(task_name):
    """手动触发任务"""
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return jsonify(result)
```

---

## 5. 任务列表

### 5.1 内置任务

| 任务名称 | 默认间隔 | 说明 |
|----------|----------|------|
| time_sync | 900秒(15分钟) | 时间同步任务 |
| cache_cleanup | 300秒(5分钟) | 缓存清理任务 |

### 5.2 扩展任务

未来可添加的任务：

| 任务名称 | 说明 |
|----------|------|
| log_cleanup | 清理过期日志文件 |
| session_cleanup | 清理过期会话 |
| backup | 数据备份任务 |
| health_check | 健康检查任务 |

---

## 6. API 文档

### 6.1 获取任务状态

```
GET /api/cron/status
```

响应示例：

```json
{
    "running": true,
    "start_time": "2026-03-14 10:00:00",
    "tasks": {
        "time_sync": {
            "name": "time_sync",
            "enabled": true,
            "interval": 900,
            "last_run": "2026-03-14 10:15:00",
            "last_status": "success",
            "last_error": null,
            "run_count": 2
        },
        "cache_cleanup": {
            "name": "cache_cleanup",
            "enabled": true,
            "interval": 300,
            "last_run": "2026-03-14 10:10:00",
            "last_status": "success",
            "last_error": null,
            "run_count": 4
        }
    }
}
```

### 6.2 手动触发任务

```
POST /api/cron/run/<task_name>
```

响应示例：

```json
{
    "success": true,
    "task": "time_sync",
    "status": "success",
    "last_run": "2026-03-14 10:16:00"
}
```

---

## 7. 后台管理界面

### 7.1 入口位置

在系统管理后台的侧边栏中添加"Cron 调度管理"入口：

```html
<!-- app/templates/core/frame_admin.html 侧边栏 -->
<a href="{{ url_for('admin.cron_manager') }}" class="nav-link">
    <i class="bi bi-clock"></i> Cron 调度管理
</a>
```

### 7.2 任务管理页面

```html
<!-- 文件路径：app/templates/core/admin/cron_manager.html -->
{% extends "core/frame_admin.html" %}

{% set show_nav = true %}
{% set show_header = true %}

{% block admin_title %}
  <title>Cron 调度管理</title>
{% endblock %}

{% block admin_content %}
<div class="container-fluid">
    <h2 class="mb-4">Cron 调度管理</h2>
    
    <div class="card">
        <div class="card-body">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>任务名称</th>
                        <th>描述</th>
                        <th>启用状态</th>
                        <th>运行间隔</th>
                        <th>上次运行</th>
                        <th>运行状态</th>
                        <th>运行次数</th>
                        <th>错误信息</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for name, task in cron_status.tasks.items() %}
                    <tr>
                        <td><strong>{{ task.name }}</strong></td>
                        <td>{{ task.description }}</td>
                        <td>
                            <div class="form-check form-switch">
                                <input class="form-check-input toggle-enabled" 
                                       type="checkbox" 
                                       data-task="{{ task.name }}"
                                       {% if task.enabled %}checked{% endif %}>
                            </div>
                        </td>
                        <td>{{ task.interval }} 秒</td>
                        <td>{{ task.last_run or '从未运行' }}</td>
                        <td>
                            {% if task.last_status == 'success' %}
                            <span class="badge bg-success">成功</span>
                            {% elif task.last_status == 'failed' %}
                            <span class="badge bg-danger">失败</span>
                            {% else %}
                            <span class="badge bg-secondary">从未运行</span>
                            {% endif %}
                        </td>
                        <td>{{ task.run_count }}</td>
                        <td>{{ task.last_error or '-' }}</td>
                        <td>
                            <button class="btn btn-sm btn-primary btn-run" data-task="{{ task.name }}">
                                立即执行
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
document.querySelectorAll('.btn-run').forEach(btn => {
    btn.addEventListener('click', async () => {
        const taskName = btn.dataset.task;
        if (!confirm(`确认立即执行任务 "${taskName}" 吗？`)) return;
        
        try {
            const resp = await fetch(`/api/cron/run/${taskName}`, { method: 'POST' });
            const data = await resp.json();
            if (data.success) {
                alert('任务执行成功');
                location.reload();
            } else {
                alert('任务执行失败: ' + data.error);
            }
        } catch (e) {
            alert('请求失败: ' + e.message);
        }
    });
});
</script>
{% endblock %}
```

### 7.3 管理路由

```python
# 文件路径：app/modules/core/cron/admin_routes.py
# 新增文件

from flask import Blueprint, render_template
from app.services.core.cron_service import get_cron_service

admin_cron_bp = Blueprint('admin_cron', __name__, url_prefix='/admin')


@admin_cron_bp.route('/cron')
def cron_manager():
    """Cron 调度管理页面"""
    cron = get_cron_service()
    status = cron.get_status()
    
    # 任务描述映射
    task_descriptions = {
        'time_sync': '时间同步任务 - 定时与远程时间服务器同步',
        'cache_cleanup': '缓存清理任务 - 清理过期的系统缓存',
    }
    
    # 添加描述信息
    for task in status['tasks'].values():
        task['description'] = task_descriptions.get(task['name'], '未知任务')
    
    return render_template('core/admin/cron_manager.html', cron_status=status)
```

### 7.4 注册蓝图

```python
# 文件路径：app/routes/__init__.py

from app.modules.core.cron.admin_routes import admin_cron_bp

# 在 register_blueprints 函数中注册
app.register_blueprint(admin_cron_bp)
```

### 7.5 页面显示字段说明

| 字段 | 来源 | 说明 |
|------|------|------|
| 任务名称 | `task.name` | 如 time_sync, cache_cleanup |
| 描述 | task_descriptions | 任务功能说明 |
| 启用状态 | `task.enabled` | 是否启用 |
| 运行间隔 | `task.interval` | 秒数 |
| 上次运行 | `task.last_run` | 时间 |
| 运行状态 | `task.last_status` | success/failed/never |
| 运行次数 | `task.run_count` | 累计执行次数 |
| 错误信息 | `task.last_error` | 上次失败原因 |

### 7.6 功能说明

1. **任务列表** - 显示所有已注册的任务
2. **启用/禁用** - 可通过开关控制任务是否执行（需扩展 API）
3. **立即执行** - 手动触发任务执行
4. **状态显示** - 成功/失败/从未运行

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-14 | 初始版本 |
| 1.1 | 2026-03-14 | 修复 Flask app context 问题，添加任务就绪标志 |
| 1.2 | 2026-03-14 | 添加后台管理界面，支持查看任务状态和手动触发 |
| 1.3 | 2026-03-14 | 添加任务启用/禁用 toggle 功能 |

---

## 9. 技术要点

### 8.1 Flask App Context 问题

后台线程无法继承 Flask 应用的 request context，需要特别注意：

1. **传递 Flask 实例** - CronService 通过 `init_app(app)` 接收 Flask 实例
2. **任务在 context 中执行** - 使用 `with self._app.app_context():` 包裹任务执行
3. **就绪标志** - `_app_ready` 标志确保应用完全初始化后才执行任务
4. **初始化顺序** - Cron 服务必须在数据库初始化之后、app 返回之前启动

### 8.2 错误处理

每个任务都有独立的异常处理：
- 任务执行失败不会影响其他任务
- 错误信息记录到 `_last_error`
- 任务状态记录到 `_last_status`

---

## 8. 待办事项

- [x] 创建 `app/services/core/tasks/` 目录
- [x] 创建任务基类 `app/services/core/tasks/base.py`
- [x] 创建时间同步任务 `app/services/core/tasks/time_sync_task.py`
- [x] 创建缓存清理任务 `app/services/core/tasks/cache_cleanup_task.py`
- [x] 创建 Cron 服务 `app/services/core/cron_service.py`
- [x] 修改 `app/services/core/time_sync_service.py` 移除内部线程
- [x] 创建 API 路由 `app/modules/core/cron/routes.py`
- [x] 注册 cron 蓝图 `app/routes/__init__.py`
- [x] 修改 `app/__init__.py` 初始化 Cron 服务
- [x] 更新系统设置页面添加任务配置
- [x] 添加任务启用/禁用 toggle API
- [x] 测试 Cron 服务功能
