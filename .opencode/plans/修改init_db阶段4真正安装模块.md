# 修改 init_db.py 阶段4 真正安装模块

**创建时间**: 2026-04-28  
**优先级**: 🔴 高  
**根本原因**: init_db.py 阶段4 只注册不安装，导致词汇表未创建

---

## 问题描述

用户反馈：
1. 导入后关系列没有内容
2. 初始化也没有创建词汇表

**根本原因**：`init_db.py` 第16-20行明确说明阶段4"不安装，不创建表"，模块安装需要用户手动操作。但用户需要在初始化时**必须完成词汇表初始化**。

---

## 当前行为 vs 期望行为

### 当前行为
```
【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）
```
- 只扫描和注册模块到数据库
- 不执行模块安装（不建表、不创建词汇表）
- 需要用户手动进入模块管理页面安装

### 期望行为
```
【阶段4】业务模块 - 扫描、注册并安装模块
```
- 自动安装所有发现的模块
- 包括建表、创建词汇表、初始化样本数据
- 确保词汇表在初始化时完成创建

---

## 修改方案

### 方案A：修改阶段4，真正安装模块（推荐）

**修改文件**: `/home/edo/cimf/init_db.py`

**修改点1**: 修改 `_init_modules_parallel()` 函数，确保真正安装

**当前代码** (第125-158行):
```python
def _init_modules_parallel(dry_run: bool) -> dict:
    """并行扫描并安装业务模块"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from core.node.services import ModuleService
    
    results = {'installed': 0, 'skipped': 0, 'success': False}
    
    if dry_run:
        results['message'] = '[模拟] 将串行注册模块'
        return results
    
    all_modules = ModuleService.scan_modules()
    
    pending_modules = [
        m for m in all_modules
        if not (m.get('is_registered') and m.get('is_installed'))
    ]
    
    results['skipped'] = len(all_modules) - len(pending_modules)
    
    if not pending_modules:
        results['success'] = True
        return results
    
    # SQLite 不支持并发写入，改用串行执行
    for m in pending_modules:
        try:
            ModuleService.register_and_install(m)
            results['installed'] += 1
        except Exception as e:
            results['error'] = str(e)
    
    results['success'] = True
    return results
```

**问题**: 虽然调用了 `register_and_install(m)`，但根据注释，这个方法可能只注册不安装。

**修改后**: 确保调用 `install_module()` 真正安装
```python
def _init_modules_parallel(dry_run: bool) -> dict:
    """扫描、注册并安装业务模块"""
    from core.node.services import ModuleService
    
    results = {'installed': 0, 'skipped': 0, 'failed': 0, 'errors': [], 'success': False}
    
    if dry_run:
        results['message'] = '[模拟] 将扫描、注册并安装模块'
        return results
    
    all_modules = ModuleService.scan_modules()
    
    for m in all_modules:
        try:
            # 先注册
            module = ModuleService.register_module(m)
            
            # 如果已安装，跳过
            if module.is_installed:
                results['skipped'] += 1
                continue
            
            # 真正安装模块（包括建表、创建词汇表）
            success, msg = ModuleService.install_module(m['id'])
            if success:
                results['installed'] += 1
                print(colored(f"    ✓ 模块 {m['id']} 安装成功", "green"))
            else:
                results['failed'] += 1
                results['errors'].append(f"{m['id']}: {msg}")
                print(colored(f"    ✗ 模块 {m['id']} 安装失败: {msg}", "red"))
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{m['id']}: {str(e)}")
            print(colored(f"    ✗ 模块 {m['id']} 安装异常: {str(e)}", "red"))
    
    results['success'] = results['failed'] == 0
    return results
```

**修改点2**: 更新阶段4的输出和注释

**修改前** (第460-481行):
```python
    # ===== 【阶段4】业务模块 =====
    print_section("阶段4：业务模块")
    
    print_step("4.1", "扫描并安装业务模块")
    try:
        if not dry_run:
            module_results = _init_modules_parallel(dry_run=False)
            
            msg = "    ✓ 业务模块扫描安装完成"
            if module_results.get('installed', 0) > 0:
                msg += f"，已安装 {module_results.get('installed')} 个"
            if module_results.get('skipped', 0) > 0:
                msg += f"，跳过 {module_results.get('skipped')} 个已安装模块"
            print(colored(msg, "green"))
            
            if module_results.get('error'):
                print(colored(f"    ⚠ 部分模块异常: {module_results.get('error')}", "yellow"))
        else:
            result = _init_modules_parallel(dry_run=True)
            print(colored(f"    {result.get('message', '[模拟]')}", "yellow"))
    except Exception as e:
        print(colored(f"    ✗ 业务模块初始化失败: {str(e)}", "red"))
```

**修改后**:
```python
    # ===== 【阶段4】业务模块 =====
    print_section("阶段4：业务模块")
    
    print_step("4.1", "扫描、注册并安装业务模块")
    try:
        if not dry_run:
            module_results = _init_modules_parallel(dry_run=False)
            
            msg = "    ✓ 业务模块处理完成"
            if module_results.get('installed', 0) > 0:
                msg += f"，已安装 {module_results.get('installed')} 个"
            if module_results.get('skipped', 0) > 0:
                msg += f"，跳过 {module_results.get('skipped')} 个"
            if module_results.get('failed', 0) > 0:
                msg += f"，失败 {module_results.get('failed')} 个"
            print(colored(msg, "green" if module_results['success'] else "yellow"))
            
            # 显示详细错误
            if module_results.get('errors'):
                for err in module_results['errors']:
                    print(colored(f"    ⚠ 失败详情: {err}", "yellow"))
            
            # 执行词汇表验证
            if module_results['success']:
                errors = verify_module_taxonomies()
                if errors:
                    print(colored(f"    ⚠ 词汇表验证失败：", "yellow"))
                    for err in errors:
                        print(colored(f"      - {err}", "yellow"))
                else:
                    print(colored("    ✓ 所有模块词汇表验证通过", "green"))
        else:
            result = _init_modules_parallel(dry_run=True)
            print(colored(f"    {result.get('message', '[模拟]')}", "yellow"))
    except Exception as e:
        print(colored(f"    ✗ 业务模块初始化失败: {str(e)}", "red"))
```

**修改点3**: 更新文件头部注释

**修改前** (第16-20行):
```python
    【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）
    
    注意：
    - 模块的安装（包括建表、初始化样本数据）在用户手动安装模块时执行
    - 使用 ./run.sh → 5 → 3 进入模块管理页面手动安装
```

**修改后**:
```python
    【阶段4】业务模块 - 扫描、注册并安装模块
    
    注意：
    - 自动安装所有发现的模块（包括建表、创建词汇表、初始化样本数据）
    - 如需手动控制，可在模块管理页面卸载不需要的模块
```

---

## 执行步骤

1. 退出计划模式
2. 修改 `init_db.py`：
   - 修改 `_init_modules_parallel()` 函数
   - 修改阶段4的输出逻辑
   - 更新文件头部注释
3. 重置数据库测试：
   ```bash
   cd /home/edo/cimf
   rm -f db.sqlite3
   ./venv/bin/python init_db.py --with-data
   ```
4. 观察输出，确认：
   - 阶段4显示"已安装 X 个"模块
   - 词汇表验证通过
5. 验证词汇表：
   ```bash
   ./venv/bin/python manage.py shell
   ```
   ```python
   from core.models import Taxonomy
   for slug in ['resident_relation', 'resident_type', 'grid', 'key_category', 'nation', 'political_status', 'marital_status', 'education', 'health_status', 'other_id_type']:
       tax = Taxonomy.objects.filter(slug=slug).first()
       count = tax.items.count() if tax else 0
       print(f"{'✓' if tax else '✗'} {slug}: {tax.name if tax else '不存在'} ({count} 项)")
   ```

---

## 修改文件清单

| 文件路径 | 修改内容 | 优先级 |
|----------|----------|--------|
| `/home/edo/cimf/init_db.py` | 修改 `_init_modules_parallel()` 真正安装模块 | 🔴 高 |
| `/home/edo/cimf/init_db.py` | 修改阶段4输出，添加详细错误信息 | 🔴 高 |
| `/home/edo/cimf/init_db.py` | 更新文件头部注释 | 🟡 中 |

---

## 预期结果

执行 `init_db.py --with-data` 后：
1. 阶段4显示安装了居民信息模块
2. 词汇表验证通过
3. 数据库中包含10个词汇表，102个词汇项
4. 导入功能正常，关系栏能正确导入

---

## 进度记录

- [ ] 编写修改计划
- [ ] 退出计划模式
- [ ] 修改 `init_db.py` 的 `_init_modules_parallel()` 函数
- [ ] 修改阶段4的输出逻辑
- [ ] 更新文件头部注释
- [ ] 重置数据库测试
- [ ] 验证词汇表创建成功
- [ ] 更新进度记录
