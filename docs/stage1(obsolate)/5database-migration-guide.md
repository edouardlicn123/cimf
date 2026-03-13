```markdown
# FFE 项目跟进系统 - 数据库迁移与管理指南

**最后更新：2026-02-12**  
**适用环境：开发、测试、生产**  
**强烈建议：每次涉及模型变更（添加/修改/删除字段、表、关系等）前都阅读本文件**

## 核心原则（必须严格遵守）

| 环境       | 允许使用 db.create_all() ? | 推荐方式                  | 禁止行为                              | 理由 / 风险                                      |
|------------|-----------------------------|---------------------------|---------------------------------------|--------------------------------------------------|
| **本地开发** | 可以（但不推荐长期使用）     | db.create_all() 或 Migrate | 频繁使用后直接上线                    | 开发阶段方便，但无法追踪变更历史                 |
| **测试/预发布** | 禁止                        | Flask-Migrate + 迁移脚本   | 直接运行 db.create_all()              | 会破坏已有数据、导致表结构不一致                 |
| **生产环境** | **绝对禁止**                | Flask-Migrate + 迁移脚本   | 任何形式的 db.create_all() 或 drop_all() | **极高风险**：会导致数据丢失、表被重建、业务中断 |

一句话总结：  
**开发阶段可以偷懒用 db.create_all()，但从第一个正式版本开始，必须全面切换到 Flask-Migrate 管理所有数据库变更。**

## 为什么 db.create_all() 在生产环境是灾难？

- 它只会创建**不存在的表**，**不会修改已存在的表结构**
- 如果你修改了模型字段（加列、改类型、加约束），它什么都不做 → 代码和数据库不一致
- 如果你删除了模型字段，它也不会删除数据库中的列 → 表结构残留垃圾字段
- 如果你删除了整个模型，它也不会删除对应的表 → 数据库中留下一堆废弃表
- 多人协作时，每个人本地 db.create_all() 后数据库结构不统一
- 生产环境直接运行会导致：**数据丢失、业务中断、回滚困难**

## 推荐的正确做法（Flask-Migrate 完整流程）

### 1. 安装依赖（只需执行一次）

```bash
pip install flask-migrate
```

### 2. 在 app/__init__.py 中集成 Flask-Migrate

```python
# app/__init__.py
from flask_migrate import Migrate

# ... 其他导入 ...

def create_app():
    app = Flask(__name__)
    # ... 配置加载、db.init_app(app) 等 ...

    # 初始化 Flask-Migrate（必须在 db.init_app 之后）
    migrate = Migrate(app, db)

    # ... 其余代码 ...
```

### 3. 常用迁移命令（记下来或做成 alias）

| 操作                               | 命令                                                                 | 说明                                           |
|------------------------------------|----------------------------------------------------------------------|------------------------------------------------|
| 初始化迁移环境（只需执行一次）      | `flask db init`                                                      | 创建 migrations/ 目录                          |
| 自动检测模型变更并生成迁移脚本      | `flask db migrate -m "添加 Project 表"`                              | 生成一个新的迁移文件（可手动修改）             |
| 应用所有未执行的迁移（升级数据库）  | `flask db upgrade`                                                   | 把迁移应用到数据库（开发/生产都用这个）        |
| 回滚到上一个版本                   | `flask db downgrade`                                                 | 回滚最近一次迁移（小心使用）                   |
| 查看当前数据库版本                 | `flask db current`                                                   | 显示当前已应用的迁移版本                       |
| 查看迁移历史                       | `flask db history`                                                   | 显示所有迁移记录                               |
| 强制标记当前数据库为最新版本       | `flask db stamp head`                                                | 用于从 db.create_all() 切换到 Migrate 时       |

### 4. 从现有 db.create_all() 项目切换到 Migrate 的正确步骤

如果你当前还在用 db.create_all()，想切换到 Migrate：

1. 确保当前数据库结构与模型完全一致（如果不一致，先手动修复或重建）
2. 运行 `flask db init`（如果 migrations/ 目录不存在）
3. 运行 `flask db migrate -m "初始迁移 - 当前表结构"`  
   → 这会生成一个包含当前所有表的迁移脚本
4. 检查生成的迁移文件（migrations/versions/xxx_initial.py），确认无误
5. 运行 `flask db stamp head`（告诉 Migrate：当前数据库已经是最新状态）
6. **以后任何模型变更都走 migrate → upgrade 流程**
7. **删除或注释掉所有 db.create_all() 调用**（尤其是生产启动脚本中）

### 5. 常见迁移场景示例

**场景1：新增字段**

```python
# models.py 修改
class Project(db.Model):
    # ... 其他字段
    budget = db.Column(db.Numeric(12, 2), nullable=True, comment="项目预算")
```

操作：
```bash
flask db migrate -m "添加 Project.budget 字段"
flask db upgrade
```

**场景2：修改字段类型（危险，需要数据迁移）**

```python
# 原：db.Column(db.Integer)
# 改：db.Column(db.BigInteger)
```

操作：
- 手动编写迁移脚本（autogenerate 可能检测不准）
- 或者先加新字段 → 数据迁移 → 删除旧字段（分步进行）

**场景3：删除字段或表**

- 不要直接删除模型字段
- 先运行 migrate 生成删除操作的脚本
- 生产环境执行前**必须备份数据库**

### 6. 生产环境上线前检查清单

- [ ] 已运行 `flask db upgrade` 到最新版本
- [ ] 所有迁移脚本已提交到 git（migrations/ 目录全部纳入版本控制）
- [ ] 生产数据库连接字符串已正确配置（环境变量）
- [ ] 启动脚本中**已删除** db.create_all()
- [ ] 首次上线前已执行 `flask db stamp head`（如果是从旧数据库迁移过来）

### 7. 团队协作提醒

- 每个人本地运行 `flask db upgrade` 保持数据库结构一致
- 迁移脚本文件名带时间戳 + 描述，commit 信息写清楚变更内容
- 多人同时改模型时，先沟通，避免冲突迁移
- 永远不要在生产服务器上运行 `flask db migrate`（只在开发机生成脚本）

**记住**：  
**db.create_all() 是开发阶段的临时工具，一旦项目进入正式迭代，必须 100% 切换到 Flask-Migrate。**
```


