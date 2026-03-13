#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code2ai.py - 项目代码收集工具（增强分离输出版）

功能概述：
将项目文件严格分为两类独立输出：
1. 参考文档文件（所有 .md 文件，无论位于哪个目录） → 输出为 xxx-doc-时间戳.md（或 xxx-doc-时间戳_partN.md）
2. 代码及其他文件（所有非 .md 文件） → 输出为 xxx-code-时间戳.md（或 xxx-code-时间戳_partN.md）

核心规则（严格遵守）：
1. 文件分类：
   - 所有以 .md 结尾的文件（不区分大小写）视为参考文档，放入 -doc- 文件
   - 其余所有文件（.py、.html、.css、.toml、.txt 等）放入 -code- 文件
2. 文件切割：
   - 每个输出文件大小控制在 400KB（400000 字节）以内
   - 切割时保证每个原始文件内容完整（不跨文件拆分单个文件）
   - 超过阈值时自动生成 part1、part2 ... 后缀
3. 文件头部内容（每个输出文件开头都包含）：
   - 项目标题 + 生成时间 + 本文件包含的文件数量说明
   - 项目目录树（简化版，突出 docs/ 和关键目录）
   - 本文件包含的文件完整列表索引（.md 文件自动提取第一行标题作为友好名称）
4. 文件内容分割标识（每个文件前）：
   - 使用 80 个 = 的强分隔线
   - 清晰标题：### 文件：相对路径
   - 行数统计
   - 再一个分隔线
5. 文件结尾统计（每个输出文件结尾）：
   - 本文件统计总结
   - 共包含 X 个文件（如果是多部分，则说明是第 N 部分）
   - 完整列出本文件包含的所有文件名
6. 排除规则（重要）：
   - 自动排除二进制文件、大文件（>524KB）、常见缓存目录
   - **强制排除输出目录 code2ai/**（防止自我包含生成的审查文件）
7. 其他特性：
   - 支持递归收集、调试日志输出
   - 文档索引优先提取标题，方便快速定位规划文档

使用方式：
    python app/utils/code2ai.py

输出示例：
    code2ai/code_for_ai_review-doc_2026-02-14_123456.md
    code2ai/code_for_ai_review-code_2026-02-14_123456.md
    （如过大：..._part1.md、..._part2.md）

注意事项：
- 优先级最高的是 docs/*.md 文件，确保规划文档始终被完整收录
- 切割只发生在文件边界，保证单个 .md 或 .py 文件内容不会被拆分到两个 txt 中
- 所有输出均为 .md 格式，便于后续阅读和复制给 AI
- 输出目录 code2ai/ 会被完全排除，避免无限递归或自我包含

"""

import os
import sys
import datetime
import fnmatch
import toml
from pathlib import Path
from typing import List, Set, Tuple


# ──────────────────────────────────────────────
# 配置读取
# ──────────────────────────────────────────────

CONFIG_FILE = "code2ai_config.toml"

try:
    config = toml.load(CONFIG_FILE)
except FileNotFoundError:
    print(f"错误：找不到配置文件 {CONFIG_FILE}！请在项目根目录创建它。")
    sys.exit(1)
except toml.TomlDecodeError as e:
    print(f"配置文件格式错误：{e}")
    sys.exit(1)

GENERAL = config.get("general", {})
INCLUDE = config.get("include", {})
EXCLUDE = config.get("exclude", {})
OUTPUT_CFG = config.get("output", {})

DEFAULT_OUTPUT_PREFIX = "code_for_ai_review"
ADD_TIMESTAMP = GENERAL.get("add_timestamp", True)
PROJECT_NAME = GENERAL.get("project_name", "Unnamed Project")
ENCODING = GENERAL.get("encoding", "utf-8")
MAX_SIZE_BYTES = GENERAL.get("max_file_size_bytes", 524288)  # 单文件跳过阈值
AUTO_IGNORE_BINARIES = GENERAL.get("auto_ignore_binaries", True)
MAX_OUTPUT_SIZE = 400 * 1024  # 400KB 单文件切割阈值

INCLUDE_PATTERNS: List[str] = INCLUDE.get("files", [])
EXCLUDE_PATTERNS: List[str] = EXCLUDE.get("patterns", [])
HEADER_STYLE = OUTPUT_CFG.get("header_style", "markdown")
FILE_SEPARATOR = "=" * 80
SHOW_LINE_NUMBERS = OUTPUT_CFG.get("show_line_numbers", False)

OUTPUT_DIR = "code2ai"


# ──────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────

def normalize_path(path: str) -> str:
    return Path(path).as_posix()


def is_excluded(path: str) -> bool:
    """判断文件是否应该被排除（更健壮版）"""
    if not os.path.isfile(path):
        return True

    rel_path = normalize_path(os.path.relpath(path))

    # 强制排除输出目录 code2ai/（防止自我包含生成的审查文件）
    if rel_path.startswith("code2ai/"):
        return True

    # 配置排除模式（大小写无关）
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(rel_path.lower(), pattern.lower()):
            return True

    # 自动忽略常见二进制扩展名
    if AUTO_IGNORE_BINARIES:
        ext = Path(path).suffix.lower()
        binary_exts = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.exe', '.bin',
                       '.woff', '.woff2', '.ttf', '.eot', '.otf', '.svg', '.map', '.min.js', '.min.css'}
        if ext in binary_exts:
            return True

    # 大小检查
    try:
        if os.path.getsize(path) > MAX_SIZE_BYTES:
            print(f"跳过大文件（>{MAX_SIZE_BYTES//1024}KB）：{rel_path}")
            return True
    except OSError:
        print(f"无法获取文件大小，跳过：{rel_path}")
        return True

    return False


def generate_tree(root: Path, prefix: str = "") -> List[str]:
    """生成简化目录树（仅显示目录和关键文件）"""
    tree = []
    items = sorted([p for p in root.iterdir() if not p.name.startswith('.')],
                   key=lambda p: (p.is_file(), p.name.lower()))
    pointers = ['├── '] * (len(items) - 1) + ['└── '] if items else []
    for pointer, item in zip(pointers, items):
        if item.name in {'__pycache__', 'venv', 'instance', 'code2ai', 'node_modules'}:
            continue
        tree.append(f"{prefix}{pointer}{item.name}")
        if item.is_dir():
            extension = '│   ' if pointer == '├── ' else '    '
            tree.extend(generate_tree(item, prefix + extension))
    return tree


def extract_title(filepath: str) -> str:
    """提取 Markdown 文件第一行标题"""
    try:
        with open(filepath, "r", encoding=ENCODING, errors="replace") as f:
            first_line = f.readline().strip()
            return first_line.lstrip("# ").strip() or Path(filepath).name
    except:
        return Path(filepath).name


def collect_files() -> Tuple[List[str], List[str]]:
    """收集文件：返回 (md_docs_files, code_other_files)"""
    root = Path.cwd()
    md_docs_files: Set[str] = set()
    code_other_files: Set[str] = set()

    all_files: Set[str] = set()

    # 按配置收集所有文件
    for pattern_str in INCLUDE_PATTERNS:
        pattern_str = pattern_str.strip()
        if not pattern_str:
            continue
        try:
            if '**' in pattern_str:
                matched = list(root.rglob(pattern_str.split('**/')[-1]))
            else:
                matched = list(root.glob(pattern_str))
            for p in matched:
                if p.is_file():
                    abs_path = str(p)
                    if not is_excluded(abs_path):
                        all_files.add(normalize_path(abs_path))
        except Exception as e:
            print(f"[WARN] pattern '{pattern_str}' 错误: {e}")

    # 严格分离：所有 .md 为文档，其余为代码/其他
    for f in all_files:
        if f.lower().endswith(".md"):
            md_docs_files.add(f)
        else:
            code_other_files.add(f)

    return sorted(md_docs_files), sorted(code_other_files)


def write_output_file(base_name: str, lines: List[str], part: int = 1):
    """写入文件（支持多部分切割）"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    suffix = f"_part{part}" if part > 1 else ""
    filename = f"{base_name}{suffix}_{timestamp}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    
    content = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    size_kb = len(content.encode('utf-8')) // 1024
    print(f"已生成：{path} （{len(lines)} 行，约 {size_kb} KB）")


def build_output(files: List[str], is_docs: bool) -> None:
    """构建并写入输出文件（支持自动切割）"""
    if not files:
        print(f"未找到{'参考文档（.md）' if is_docs else '代码及其他'}文件，跳过输出")
        return
    
    output_lines = []
    
    # 开头信息
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_lines.extend([
        f"# {PROJECT_NAME} - {'参考文档快照（所有 .md 文件）' if is_docs else '代码及其他文件快照（非 .md）'}",
        f"# 生成时间：{now}",
        f"# 本文件包含 {len(files)} 个{'参考文档（.md）' if is_docs else '代码及其他'}文件",
        "",
    ])
    
    # 目录树
    output_lines.append("### 项目目录树（关键结构）\n")
    tree = generate_tree(Path.cwd())
    output_lines.extend(tree[:150])
    output_lines.append("\n")
    
    # 文件索引
    section = "参考文档（.md）" if is_docs else "代码及其他文件"
    output_lines.append(f"### 本文件包含的 {section} 列表（共 {len(files)} 个）\n")
    for f in files:
        rel = os.path.relpath(f)
        if is_docs:
            title = extract_title(f)
            output_lines.append(f"- [{title}]({rel})")
        else:
            output_lines.append(f"- {rel}")
    output_lines.append("\n")
    
    # 开始添加文件内容
    current_lines = output_lines.copy()
    current_size = len("\n".join(current_lines).encode('utf-8'))
    part = 1
    
    for filepath in files:
        try:
            with open(filepath, "r", encoding=ENCODING, errors="replace") as f:
                content = f.read()
            rel_path = os.path.relpath(filepath)
            lines = content.splitlines()
            line_count = len(lines)
            
            # 强分割标识
            separator = [
                "",
                FILE_SEPARATOR,
                f"### 文件：{rel_path}",
                f"行数：{line_count}",
                FILE_SEPARATOR,
                "",
            ]
            if SHOW_LINE_NUMBERS:
                numbered = "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
            else:
                numbered = content.rstrip()
                
            file_content = separator + [numbered, ""]
            file_size = len("\n".join(file_content).encode('utf-8'))
            
            # 检查是否需要切割
            if current_size + file_size > MAX_OUTPUT_SIZE:
                # 写入当前部分（包含结尾统计）
                current_lines.extend([
                    "",
                    FILE_SEPARATOR,
                    f"### 本文件统计总结（第 {part} 部分）",
                    f"本部分包含 {len(files)} 个文件中的前一部分",
                    ""
                ])
                write_output_file(f"{DEFAULT_OUTPUT_PREFIX}_{'doc' if is_docs else 'code'}", current_lines, part)
                
                # 新部分重置
                part += 1
                current_lines = output_lines.copy()
                current_size = len("\n".join(current_lines).encode('utf-8'))
            
            current_lines.extend(file_content)
            current_size += file_size
            print(f"已添加：{rel_path}")
            
        except Exception as e:
            print(f"读取失败 {filepath}：{e}")
    
    # 最终部分结尾统计（完整列表）
    current_lines.extend([
        "",
        FILE_SEPARATOR,
        f"### 本文件统计总结（第 {part} 部分）",
        f"共包含 {len(files)} 个{'参考文档（.md）' if is_docs else '代码及其他'}文件：",
        ""
    ] + [f"- {os.path.relpath(f)}" for f in files] + [""])
    
    write_output_file(f"{DEFAULT_OUTPUT_PREFIX}_{'doc' if is_docs else 'code'}", current_lines, part)


def main():
    print("开始收集代码与文档用于 AI 审查（严格分离 .md 与其他文件）...")
    
    md_docs_files, code_other_files = collect_files()
    
    print(f"\n[统计] 参考文档（.md 文件）：{len(md_docs_files)} 个")
    print(f"[统计] 代码及其他文件：{len(code_other_files)} 个\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    build_output(md_docs_files, is_docs=True)
    build_output(code_other_files, is_docs=False)
        
    print("\n所有文件生成完成！")


if __name__ == "__main__":
    main()
