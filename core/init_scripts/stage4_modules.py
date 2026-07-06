"""
================================================================================
文件：stage4_modules.py
路径：/home/edo/cimf/core/init_scripts/stage4_modules.py
================================================================================

功能说明：
    初始化流程的阶段4：业务模块扫描与注册。

    负责扫描 modules/ 目录下的所有业务模块，并注册到数据库中。
    注意：此阶段仅注册模块（is_installed=False），不执行模块安装。

    模块安装（建表、初始化数据）需要用户在模块管理页面手动触发。

    当前实现：
    - 扫描 modules/ 目录，读取每个模块的 module.py
    - 解析 MODULE_INFO 字典，提取模块信息
    - 注册到 Module 模型（如果已注册则更新信息）
    - 验证已安装模块的词汇表完整性

主要功能：
    - run_stage4(): 执行阶段4的主函数
    - 扫描并注册所有未注册的模块
    - 验证已安装模块的词汇表（verify_module_taxonomies）
    - 提供详细的执行进度输出

用法：
    1. 通过 init_db.py 调用：
       python init_db.py --stage 4

    2. 直接调用：
       from core.init_scripts.stage4_modules import run_stage4
       results = run_stage4(dry_run=False)
       # results = {'installed': 1, 'skipped': 3, 'error': None}

性能目标：
    - 扫描并注册4个模块：< 2秒
    - 词汇表验证：< 0.5秒

版本：
    - 1.0: 从 init_db.py 拆分，独立为阶段文件

依赖：
    - core.node.services.ModuleService
    - core.init_scripts.common（print_section, print_step, colored, verify_module_taxonomies）
    - core.models.Module

注意：
    - 此阶段不会自动安装模块（is_installed 保持 False）
    - 模块安装需要在模块管理页面手动触发
    - 如果模块词汇表验证失败，会显示警告但不会中断执行
    - SQLite 不支持并发，使用串行执行
"""

from typing import Any

from core.init_scripts.common import colored, print_section, print_step, verify_module_taxonomies


def run_stage4(dry_run: bool = False) -> dict[str, Any]:
    """
    执行阶段4：扫描并注册业务模块

    Args:
        dry_run: 是否模拟执行

    Returns:
        dict: 模块注册结果
    """
    print_section("阶段4：业务模块")
    print_step("4.1", "扫描并注册业务模块")

    from core.module.services import ModuleService  # noqa: PLC0415

    if dry_run:
        return {"message": "[模拟] 将扫描并注册模块", "success": True}

    # 使用通用函数，执行扫描+注册+安装
    # 初始化阶段尊重install_on_init设置，不自动安装该参数为False的模块
    result = ModuleService.scan_register_install(do_install=True, dry_run=False, respect_install_on_init=True)

    # 转换为阶段4结果格式
    return {
        "installed": result.get("installed", 0),
        "skipped": result.get("skipped", 0),
        "success": len(result.get("failed", [])) == 0,
        "failed": result.get("failed", []),
    }


def print_module_results(results: dict[str, Any]):
    """打印模块注册结果"""
    msg = "    ✓ 业务模块扫描注册完成"
    if results.get("installed", 0) > 0:
        msg += f"，已注册 {results.get('installed')} 个"
    if results.get("skipped", 0) > 0:
        msg += f"，跳过 {results.get('skipped')} 个已注册模块"
    print(colored(msg, "green"))

    if results.get("error"):
        print(colored(f"    ⚠ 部分模块异常: {results.get('error')}", "yellow"))


def verify_installed_modules():
    """验证已安装模块的词汇表"""
    print_section("验证模块词汇表")
    print_step("5.1", "验证已安装模块的词汇表")

    errors = verify_module_taxonomies()
    if errors:
        print(colored("  ⚠ 词汇表验证失败：", "yellow"))
        for err in errors:
            print(colored(f"    - {err}", "yellow"))
    else:
        print(colored("  ✓ 所有模块词汇表验证通过", "green"))
